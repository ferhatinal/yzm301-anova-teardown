"""Takım ailesi: F testi, tek yönlü sabit etkili ANOVA (üç tedavi kolu: groups=3).

Kapsam notu (temiz oda): Bu dosya yalnızca [DOK] düzeyindeki bilgiden yazıldı:
  etki büyüklüğü f (Cohen), merkezsel olmayan F dağılımı,
  df1 = k-1, df2 = N-k, ncp = f^2 * N, kritik F = F^{-1}(1-alpha; df1, df2).
HIPOTEZ etiketli satırlar kanıtlanmış davranış DEĞİLDİR; REA oturumunda
(LEDGER.md) [REA] olarak doğrulanana ya da oracle/ vektörleriyle sınanana kadar
[AJAN] varsayımıdır. Çıktı alan adları da CONTRACT.md gelene kadar VARSAYIMDIR.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy import stats

from ..errors import InputError
from ..robust import ncf_cdf

# HIPOTEZ H-07: a priori toplam N, grup sayısının katına yukarı yuvarlanır
# (n_total = groups * n_per_group). False ise N 1'er artırılarak aranır.
ROUND_TO_MULTIPLE_OF_GROUPS = True
MIN_PER_GROUP = 2        # HIPOTEZ H-03
MIN_GROUPS = 2           # HIPOTEZ H-08
MAX_TOTAL = 20_000_000   # HIPOTEZ H-06


@dataclass(frozen=True)
class AnovaResult:
    groups: int
    n_total: int
    actual_power: float
    critical: float
    df1: int
    df2: int
    ncp: float

    def as_contract_dict(self) -> dict:
        per = self.n_total // self.groups if self.n_total % self.groups == 0 else None
        return {
            "n_per_group": per,
            "n_total": self.n_total,
            "actual_power": round(self.actual_power, 4),
            "critical": round(self.critical, 4),
            "df1": self.df1,
            "df2": self.df2,
            "ncp": round(self.ncp, 4),
        }


LO_PROB, HI_PROB = 1e-7, 0.9999999     # [REA] LEDGER R36
F_MAX = 50.0                           # [REA] R30
F_MIN_A_PRIORI = 1e-6                  # [REA] R30


def _check(f, alpha, groups, a_priori=True):
    if not isinstance(groups, int) or isinstance(groups, bool) or groups < MIN_GROUPS:
        raise InputError("There must be at least 2 groups (groups tam sayı >= 2 olmalı)")
    lo = F_MIN_A_PRIORI if a_priori else 0.0
    if not math.isfinite(f) or f < lo or f > F_MAX:
        raise InputError(f"f [{lo:g}, {F_MAX:g}] aralığında olmalı")
    if not (math.isfinite(alpha) and LO_PROB <= alpha <= HI_PROB):
        raise InputError("alpha [1e-7, 0.9999999] aralığında olmalı")


def anova_power(f: float, alpha: float, groups: int, n_total: int):
    """(power, critical, df1, df2, ncp)."""
    df1 = groups - 1
    df2 = n_total - groups
    if df2 < 1:
        raise InputError("n_total, groups değerinden büyük olmalı")
    ncp = f * f * n_total
    crit = float(stats.f.ppf(1 - alpha, df1, df2))
    power = 1.0 - ncf_cdf(crit, df1, df2, ncp)
    if not math.isfinite(power):
        raise InputError("güç hesabı sayısal olarak çözülemedi")
    return power, crit, df1, df2, ncp


def a_priori(f: float, alpha: float, power: float, groups: int) -> AnovaResult:
    _check(f, alpha, groups)
    if not (math.isfinite(power) and LO_PROB <= power <= HI_PROB):
        raise InputError("power [1e-7, 0.9999999] aralığında olmalı")
    if power < alpha:
        raise InputError("Power must be greater than or equal to alpha")  # [REA] R6

    def total(m: int) -> int:          # m. aday toplam N (m = 1, 2, 3, ...)
        if ROUND_TO_MULTIPLE_OF_GROUPS:
            return groups * (MIN_PER_GROUP + m - 1)
        return groups + m              # n_total = groups + 1, groups + 2, ...

    def reached(m: int) -> bool:
        return anova_power(f, alpha, groups, total(m))[0] >= power

    # HIPOTEZ H-02: koşulu sağlayan ilk (en küçük) N; üstel + ikili arama, ardından
    # küçük pencerede yeniden doğrulama.
    lo = 1
    if reached(lo):
        m = lo
    else:
        hi = 2
        while not reached(hi):
            lo, hi = hi, hi * 2
            if total(hi) > MAX_TOTAL:
                raise InputError("gerekli örneklem büyüklüğü sınırı aşıyor")
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if reached(mid):
                hi = mid
            else:
                lo = mid
        m = hi
        for cand in range(max(1, m - 10), m):
            if reached(cand):
                m = cand
                break
    n_total = total(m)
    pw, crit, df1, df2, ncp = anova_power(f, alpha, groups, n_total)
    return AnovaResult(groups, n_total, pw, crit, df1, df2, ncp)


def post_hoc(f: float, alpha: float, groups: int, n_total: int) -> AnovaResult:
    _check(f, alpha, groups, a_priori=False)
    if not isinstance(n_total, int) or isinstance(n_total, bool) or n_total <= groups:
        raise InputError("n_total, groups değerinden büyük bir tam sayı olmalı")  # HIPOTEZ H-03
    pw, crit, df1, df2, ncp = anova_power(f, alpha, groups, n_total)
    return AnovaResult(groups, n_total, pw, crit, df1, df2, ncp)
