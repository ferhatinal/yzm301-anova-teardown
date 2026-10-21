"""Diferansiyel test: aynı girdiler iki sisteme, çıktılar karşılaştırılır.

İki katmanlı kâhin (ödev: 'UYGULAMA KISITLARI / c'):
  1) oracle/gpower_<aile>.csv   -> G*Power arayüzünden elle toplanan vektörler (asıl kâhin)
  2) oracle/library_<aile>.csv  -> statsmodels ile üretilen 500+ ölçek vektörü (yardımcı kâhin)

Kullanım:
  python tests/differential.py gpower  [aile]   # varsayılan aile: anova-oneway
  python tests/differential.py library [aile]
  python tests/differential.py generate [aile]  # library CSV'sini yeniden üret

Tolerans (ödev e): N, n1, n2, df TAM; diğer alanlar karşılaştırma basamağına kadar.
Her uyuşmazlık raporlanır; açıklaması elle yazılır (tests/REPORT.md).
"""

from __future__ import annotations

import csv
import itertools
import math
import os
import sys
import warnings

import _path  # noqa: F401

warnings.filterwarnings("ignore")

from powerlab import engine  # noqa: E402

ORACLE = os.path.join(_path.ROOT, "oracle")
DEFAULT_FAMILY = "anova-oneway"

# aile -> mod -> (girdi alanı, tip)
INPUTS = {
    "anova-oneway": {
        "a-priori": [("f", float), ("alpha", float), ("power", float), ("groups", int)],
        "post-hoc": [("f", float), ("alpha", float), ("groups", int), ("n_total", int)],
    },
    "t2-indep": {
        "a-priori": [("tails", int), ("d", float), ("alpha", float), ("power", float), ("ratio", float)],
        "post-hoc": [("tails", int), ("d", float), ("alpha", float), ("n1", int), ("n2", int)],
    },
}
INT_OUT = ("n1", "n2", "n_total", "n_per_group", "df", "df1", "df2")
DEC_OUT = {"actual_power": 4, "critical": 4, "ncp": 4}  # sözleşme çıktısı 4 basamak; ekrana göre güncelle


def _blank(x):
    return x in ("", None)


def run_engine(family, row):
    params = {}
    for name, typ in INPUTS[family][row["mode"]]:
        if not _blank(row.get(name)):
            params[name] = typ(float(row[name])) if typ is int else typ(row[name])
    try:
        return engine.compute(family, row["mode"], params)
    except engine.InputError as e:
        return {"error": str(e)}


def compare(row, got):
    """[(alan, kâhin, motor), ...] uyuşmazlıkları. a-priori'de n_total/n1/n2 satırdaki değer BEKLENEN çıktıdır."""
    if row.get("expect_error") == "1":
        return [] if "error" in got else [("hata", "bekleniyordu", "alınmadı")]
    if "error" in got:
        return [("hata", "değer", got["error"])]
    diffs = []
    for k in INT_OUT:
        if k in got and not _blank(row.get(k)) and got[k] is not None and int(float(row[k])) != got[k]:
            diffs.append((k, int(float(row[k])), got[k]))
    for k, dec in DEC_OUT.items():
        if k in got and not _blank(row.get(k)):
            v = float(row[k])
            if not math.isclose(round(v, dec), got[k], abs_tol=10 ** -dec / 2 + 1e-12):
                diffs.append((k, v, got[k]))
    return diffs


def evaluate(path, family):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("test") == family]
    ok, mism = 0, []
    for r in rows:
        diffs = compare(r, run_engine(family, r))
        if diffs:
            mism.append((r, diffs))
        else:
            ok += 1
    return len(rows), ok, mism


def _classify(family, row, diffs):
    """Bilinen, açıklanmış uyuşmazlık sınıfı (yoksa None)."""
    if not str(row.get("source", "")).startswith("statsmodels") or len(diffs) != 1:
        return None
    field, oracle, mine = diffs[0]
    if family == "anova-oneway" and field == "n_total":
        k = int(float(row["groups"]))
        if mine % k == 0 and 0 <= mine - oracle < k and mine == k * math.ceil(oracle / k):
            return "H-07: kütüphane toplam N'yi 1'er artırır, motor grup sayısının katına yukarı yuvarlar"
    if family == "t2-indep" and field == "n1" and float(row.get("ratio") or 1) != 1 and oracle - mine == 1:
        return "H-01: kütüphane n2'yi kesirli bırakır, motor n2'yi yukarı yuvarlar"
    return None


def report(path, family):
    if not os.path.exists(path):
        print(f"{os.path.basename(path)}: dosya yok")
        return 1
    total, ok, mism = evaluate(path, family)
    if total == 0:
        print(f"{os.path.basename(path)}: bu aile için vektör yok")
        return 1
    print(f"{os.path.basename(path)} [{family}]: {total} vektör | tam uyum {ok}/{total} ({100 * ok / total:.1f}%)")
    classes, unexplained = {}, []
    for r, diffs in mism:
        c = _classify(family, r, diffs)
        if c:
            classes[c] = classes.get(c, 0) + 1
        else:
            unexplained.append((r, diffs))
    for c, n in classes.items():
        print(f"  AÇIKLANMIŞ ({n}): {c}")
    for r, diffs in unexplained[:25]:
        key = {k: r[k] for k, _ in INPUTS[family][r["mode"]] if not _blank(r.get(k))}
        print("  AÇIKLANMAMIŞ UYUŞMAZLIK", key, "->", "; ".join(f"{a}: kâhin={o} motor={m}" for a, o, m in diffs))
    if len(unexplained) > 25:
        print(f"  ... {len(unexplained) - 25} açıklanmamış uyuşmazlık daha")
    print(f"  açıklanmamış uyuşmazlık: {len(unexplained)}")
    return 0 if not unexplained else 1


# --------------------------------------------------------------------------
# Kütüphane kâhini (statsmodels): N kesirli verir; biz tavana alıp karşılaştırırız.
# G*Power yukarı yuvarlar, kütüphane yuvarlamaz: bu fark ödevin istediği bulgudur.
# --------------------------------------------------------------------------

LIB_FIELDS = ["test", "mode", "f", "alpha", "power", "groups", "n_total", "n_per_group",
              "df1", "df2", "actual_power", "critical", "ncp", "source", "note"]
T2_FIELDS = ["test", "mode", "tails", "d", "alpha", "power", "ratio", "n1", "n2", "n_total",
             "actual_power", "critical", "df", "ncp", "source", "note"]


def generate_library(family):
    rows = []
    skipped = 0
    if family == "anova-oneway":
        from statsmodels.stats.power import FTestAnovaPower
        solver = FTestAnovaPower()
        grid = itertools.product((0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.8, 1.0),
                                 (0.01, 0.05, 0.1), (0.8, 0.9, 0.95, 0.99), (2, 3, 4, 5, 6))
        for f, alpha, power, k in grid:
            try:
                n_frac = float(solver.solve_power(effect_size=f, alpha=alpha, power=power, k_groups=k))
            except Exception:
                skipped += 1
                continue
            if not math.isfinite(n_frac) or n_frac <= 0:
                skipped += 1
                continue
            rows.append({"test": family, "mode": "a-priori", "f": f, "alpha": alpha, "power": power,
                         "groups": k, "n_total": math.ceil(n_frac - 1e-9),
                         "source": "statsmodels.FTestAnovaPower",
                         "note": f"n_total_fractional={n_frac:.6f}"})
        fields = LIB_FIELDS
    else:
        from statsmodels.stats.power import TTestIndPower
        solver = TTestIndPower()
        grid = itertools.product((0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0), (0.01, 0.05, 0.1),
                                 (0.8, 0.9, 0.95, 0.99), (0.5, 1.0, 2.0, 3.0), (1, 2))
        for d, alpha, power, ratio, tails in grid:
            alt = "two-sided" if tails == 2 else "larger"
            try:
                n_frac = float(solver.solve_power(effect_size=d, alpha=alpha, power=power, ratio=ratio, alternative=alt))
            except Exception:
                skipped += 1
                continue
            if not math.isfinite(n_frac) or n_frac <= 0:
                skipped += 1
                continue
            rows.append({"test": family, "mode": "a-priori", "tails": tails, "d": d, "alpha": alpha,
                         "power": power, "ratio": ratio, "n1": math.ceil(n_frac - 1e-9),
                         "source": "statsmodels.TTestIndPower", "note": f"n1_fractional={n_frac:.6f}"})
        fields = T2_FIELDS
    path = os.path.join(ORACLE, f"library_{family}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} kütüphane vektörü yazıldı ({skipped} atlandı): {path}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "gpower"
    fam = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_FAMILY
    if fam not in INPUTS:
        print(__doc__)
        sys.exit(2)
    if mode == "generate":
        generate_library(fam)
    elif mode in ("library", "gpower"):
        sys.exit(report(os.path.join(ORACLE, f"{mode}_{fam}.csv"), fam))
    else:
        print(__doc__)
        sys.exit(2)
