"""İnce CLI adaptörü. Hesap yok: argüman ayrıştır, engine.compute çağır, JSON yaz.

Sözleşme (ödev metni):
  başarı : tek satır JSON, çıkış kodu 0
  hata   : {"error": "<açıklama>"} ve sıfırdan farklı çıkış kodu (2 girdi, 3 aile)

Örnek:
  gpower-clone --test anova-oneway --mode a-priori --f 0.25 --groups 3 --alpha 0.05 --power 0.95
"""

from __future__ import annotations

import argparse
import json
import sys

from . import engine


class _JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):  # argparse varsayılanı stderr'e yazar; sözleşme JSON ister
        _emit({"error": message})
        sys.exit(2)


def _emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    p = _JsonArgumentParser(prog="gpower-clone")
    p.add_argument("--test", required=True)
    p.add_argument("--mode", required=True, choices=["a-priori", "post-hoc"])
    p.add_argument("--alpha", type=float)
    p.add_argument("--power", type=float)
    # ANOVA ailesi
    p.add_argument("--f", type=float, dest="f")
    p.add_argument("--groups", type=int)
    p.add_argument("--n-total", type=int, dest="n_total")
    # t2-indep (referans)
    p.add_argument("--tails", type=int)
    p.add_argument("--d", type=float)
    p.add_argument("--ratio", type=float)
    p.add_argument("--n1", type=int)
    p.add_argument("--n2", type=int)
    return p


def run(argv=None) -> int:
    args = vars(build_parser().parse_args(argv))
    test, mode = args.pop("test"), args.pop("mode")
    params = {k: v for k, v in args.items() if v is not None}
    try:
        _emit(engine.compute(test, mode, params))
        return 0
    except engine.UnsupportedFamily as e:
        _emit({"error": str(e)})
        return 3
    except engine.InputError as e:
        _emit({"error": str(e)})
        return 2


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
