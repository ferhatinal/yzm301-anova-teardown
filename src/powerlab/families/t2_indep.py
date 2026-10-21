"""REFERANS aile: t testi, iki bağımsız ortalama.

Bu aile yalnızca ödev sözleşmesindeki örnek çıktıyı ([DOK]) kullanarak CLI/JSON
biçimini regresyonda sabitlemek için tutulur. Takımın asıl ailesi anova_oneway'dir.
Her takım yalnızca kendi ailesini gerçekler: teslimden önce bu dosyayı ve
FAMILIES kaydını silebilirsin (tests/test_t2_reference.py de silinir).

HIPOTEZ etiketli satırlar kanıtlanmış davranış DEĞİLDİR ([AJAN] varsayımı).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy import stats

from ..errors import InputError
from ..robust import nct_cdf

MAX_N = 10_000_000  # HIPOTEZ H-06
MIN_N = 2           # HIPOTEZ H-03


@dataclass(frozen=True)
class T2Result:
    n1: int
    n2: int
    actual_power: float
    critical: float
    df: int
    ncp: float

    def as_contract_dict(self) -> dict:
        return {
            "n1": self.n1, "n2": self.n2, "n_total": self.n1 + self.n2,
            "actual_power": round(self.actual_power, 4),
            "critical": round(self.critical, 4),
            "df": self.df, "ncp": round(self.ncp, 4),
        }


def _check(tails, d, alpha):
    if tails not in (1, 2):
        raise InputError("tails 1 ya da 2 olmalı")
    if not math.isfinite(d) or d == 0:
        raise InputError("d sonlu ve sıfırdan farklı olmalı")
    if not (0 < alpha < 1):
        raise InputError("alpha (0,1) aralığında olmalı")


def t2_power(tails, d, alpha, n1, n2):
    d = abs(d)  # HIPOTEZ H-04
    df = n1 + n2 - 2
    ncp = d * math.sqrt(n1 * n2 / (n1 + n2))
    if tails == 2:
        crit = float(stats.t.ppf(1 - alpha / 2, df))
        power = (1.0 - nct_cdf(crit, df, ncp)) + nct_cdf(-crit, df, ncp)
    else:
        crit = float(stats.t.ppf(1 - alpha, df))
        power = 1.0 - nct_cdf(crit, df, ncp)
    if not math.isfinite(power):
        raise InputError("güç hesabı sayısal olarak çözülemedi")
    return power, crit, df, ncp


def _n2_from(n1, ratio):
    return max(MIN_N, math.ceil(n1 * ratio - 1e-12))  # HIPOTEZ H-01


def a_priori(tails, d, alpha, power, ratio=1.0) -> T2Result:
    _check(tails, d, alpha)
    if not (0 < power < 1):
        raise InputError("power (0,1) aralığında olmalı")
    if power <= alpha:
        raise InputError("power, alpha değerinden büyük olmalı")  # HIPOTEZ H-05
    if not math.isfinite(ratio) or ratio <= 0:
        raise InputError("ratio (n2/n1) sıfırdan büyük olmalı")

    def reached(n1):
        return t2_power(tails, d, alpha, n1, _n2_from(n1, ratio))[0] >= power

    lo = MIN_N
    if reached(lo):
        n1 = lo
    else:
        hi = lo * 2
        while not reached(hi):
            lo, hi = hi, hi * 2
            if hi > MAX_N:
                raise InputError("gerekli örneklem büyüklüğü sınırı aşıyor")
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if reached(mid):
                hi = mid
            else:
                lo = mid
        n1 = hi
        for cand in range(max(MIN_N, n1 - 10), n1):  # HIPOTEZ H-02: ilk sağlayan n
            if reached(cand):
                n1 = cand
                break
    n2 = _n2_from(n1, ratio)
    pw, crit, df, ncp = t2_power(tails, d, alpha, n1, n2)
    return T2Result(n1, n2, pw, crit, df, ncp)


def post_hoc(tails, d, alpha, n1, n2) -> T2Result:
    _check(tails, d, alpha)
    if n1 < MIN_N or n2 < MIN_N:
        raise InputError(f"n1 ve n2 en az {MIN_N} olmalı")
    pw, crit, df, ncp = t2_power(tails, d, alpha, n1, n2)
    return T2Result(n1, n2, pw, crit, df, ncp)
