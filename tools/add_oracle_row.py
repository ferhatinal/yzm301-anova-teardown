"""G*Power ekranından okuduğun bir sonucu oracle CSV'sine güvenli biçimde ekler.

Elle CSV düzenlemek sütun kaydırma hatasına açıktır. Bu betik başlığı korur, alanları doğrular,
ekran görüntüsü dosyasının VARLIĞINI kontrol eder ve satırı hemen motorla karşılaştırır
(uyuşmazlık varsa hemen görürsün). Değerleri G*Power ekranından OKUDUĞUN gibi yaz.

Örnekler (yalnızca biçim gösterir; sayıları kendi ekranından al):
  python tools/add_oracle_row.py a-priori --f 0.25 --alpha 0.05 --power 0.80 --groups 3 \
      --n-total <ekrandaki Total sample size> --df1 <..> --df2 <..> --actual-power <..> \
      --critical <..> --ncp <..> --screenshot oracle/screens/001.png

  python tools/add_oracle_row.py post-hoc --f 0.25 --alpha 0.05 --groups 3 --n-total 90 \
      --actual-power <ekrandaki Power (1-β err prob)> --critical <..> --ncp <..> --df1 2 --df2 87 \
      --screenshot oracle/screens/002.png

  python tools/add_oracle_row.py a-priori --f 0 --alpha 0.05 --power 0.8 --groups 3 \
      --expect-error --note "G*Power'ın verdiği hata iletisi" --screenshot oracle/screens/003.png
"""

import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import differential as D  # noqa: E402

PATH = os.path.join(ROOT, "oracle", "gpower_anova-oneway.csv")
HEADER = ["test", "mode", "f", "alpha", "power", "groups", "n_total", "n_per_group", "df1", "df2",
          "actual_power", "critical", "ncp", "source", "note", "screenshot", "expect_error"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["a-priori", "post-hoc"])
    for name in ("f", "alpha", "power", "n_total", "n_per_group", "df1", "df2", "actual_power", "critical", "ncp"):
        ap.add_argument("--" + name.replace("_", "-"), dest=name)
    ap.add_argument("--groups")
    ap.add_argument("--note", default="")
    ap.add_argument("--screenshot", default="")
    ap.add_argument("--expect-error", action="store_true")
    ap.add_argument("--no-screenshot-check", action="store_true")
    a = ap.parse_args()

    need_in = {"a-priori": ("f", "alpha", "power", "groups"), "post-hoc": ("f", "alpha", "groups", "n_total")}[a.mode]
    missing = [k for k in need_in if getattr(a, k) is None]
    if missing:
        sys.exit("Eksik girdi: " + ", ".join("--" + m.replace("_", "-") for m in missing))
    if not a.expect_error:
        need_out = ("n_total", "actual_power", "critical", "ncp", "df1", "df2") if a.mode == "a-priori" else \
                   ("actual_power", "critical", "ncp", "df1", "df2")
        miss = [k for k in need_out if getattr(a, k) is None]
        if miss:
            sys.exit("Ekrandan okunan çıktı eksik: " + ", ".join("--" + m.replace("_", "-") for m in miss))
    if not a.screenshot and not a.no_screenshot_check:
        sys.exit("--screenshot gerekli (ödev: her vektör ekran görüntüsüyle).")
    if a.screenshot and not a.no_screenshot_check and not os.path.exists(os.path.join(ROOT, a.screenshot)):
        sys.exit(f"Ekran görüntüsü bulunamadı: {a.screenshot}")

    row = {k: "" for k in HEADER}
    row.update({"test": "anova-oneway", "mode": a.mode, "source": "gpower-3.1.9.7-gui", "note": a.note,
                "screenshot": a.screenshot, "expect_error": "1" if a.expect_error else ""})
    for k in ("f", "alpha", "power", "groups", "n_total", "n_per_group", "df1", "df2", "actual_power", "critical", "ncp"):
        v = getattr(a, k)
        if v is not None:
            row[k] = v
    if a.mode == "a-priori" and row["n_total"] and not row["n_per_group"] and not a.expect_error:
        n, k = int(float(row["n_total"])), int(float(row["groups"]))
        if n % k == 0:
            row["n_per_group"] = n // k

    new_file = not os.path.exists(PATH) or os.path.getsize(PATH) == 0
    with open(PATH, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        if new_file:
            w.writeheader()
        w.writerow(row)

    got = D.run_engine("anova-oneway", row)
    diffs = D.compare(row, got)
    print("Satır eklendi:", PATH)
    if diffs:
        print("MOTORLA UYUŞMUYOR:")
        for field, oracle, mine in diffs:
            print(f"  {field}: G*Power={oracle}  motor={mine}")
        print("İpucu: n_total farkı grup sayısına bağlıysa tests/REPORT.md ve ROUND_TO_MULTIPLE_OF_GROUPS'a bak.")
        return 1
    print("Motorla uyumlu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
