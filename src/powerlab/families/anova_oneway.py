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


# --- Nihai hesap: temiz oda oturumunun (yalniz SPEC.md'den yazilan) modulu ---------------
# `_anova_clean.py` degistirilmeden kopyalandi (cleanroom/anova_clean.py ile ayni). Yukaridaki
# `anova_power` ve sabitler iskeletten kalma referanstir; testler onu ikinci yol olarak kullanir.
from . import _anova_clean as _clean


def _wrap(groups, d):
    return AnovaResult(groups, int(d["n_total"]), float(d["actual_power"]), float(d["critical"]),
                       int(d["df1"]), int(d["df2"]), float(d["ncp"]))


def a_priori(f: float, alpha: float, power: float, groups: int) -> AnovaResult:
    _check(f, alpha, groups)   # tip/aralik on denetimi (InputError); gerisi temiz oda modulunde
    try:
        return _wrap(groups, _clean.a_priori(f, alpha, power, groups))
    except ValueError as e:
        raise InputError(str(e)) from e


def post_hoc(f: float, alpha: float, groups: int, n_total: int) -> AnovaResult:
    _check(f, alpha, groups, a_priori=False)
    if not isinstance(n_total, int) or isinstance(n_total, bool) or n_total <= groups:
        raise InputError("Sample size must be greater than the number of groups (k)")  # [REA] R5
    try:
        return _wrap(groups, _clean.post_hoc(f, alpha, groups, n_total))
    except ValueError as e:
        raise InputError(str(e)) from e
