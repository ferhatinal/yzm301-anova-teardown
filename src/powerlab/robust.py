"""Sağlam dağılım yardımcıları: NaN'a karşı korumalı CDF'ler.

BULGU (HALLUCINATIONS.md H-A): scipy.stats.nct.cdf bazı (df, ncp, x<0)
kombinasyonlarında (ör. df=254, ncp=6.4, x=-2.595) NaN döndürür. NaN
karşılaştırmada sessizce False olduğundan N araması yanlış sonuca gidiyordu.
Bu modül her CDF için bir geri-dönüş zinciri kullanır ve hiçbir yol sonlu bir
değer vermezse sessizce yanlış sonuç üretmek yerine InputError fırlatır.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import integrate, special, stats

from .errors import InputError


def _clip01(v: float) -> float:
    return min(1.0, max(0.0, v))


def nct_cdf(x: float, df: int, ncp: float) -> float:
    """Merkezsel olmayan t CDF'i."""
    for fn in (lambda: float(special.nctdtr(df, ncp, x)), lambda: float(stats.nct.cdf(x, df, ncp))):
        try:
            v = fn()
        except Exception:
            continue
        if math.isfinite(v):
            return _clip01(v)
    # son çare: P(T<=x) = ∫ Phi(x*sqrt(v/df) - ncp) f_chi2(v) dv
    f = lambda v: stats.norm.cdf(x * math.sqrt(v / df) - ncp) * stats.chi2.pdf(v, df)
    val, _ = integrate.quad(f, 0, 12 * df + 100, limit=400, epsabs=1e-14, epsrel=1e-12)
    if not math.isfinite(val):
        raise InputError("güç hesabı sayısal olarak çözülemedi")
    return _clip01(val)


def ncf_cdf_poisson(x: float, dfn: float, dfd: float, nc: float) -> float:
    """Merkezsel olmayan F CDF'i, Poisson-beta karışımı ile (bağımsız yol).

    P(F<=x) = sum_j Pois(j; nc/2) * I_y(dfn/2 + j, dfd/2),  y = dfn*x/(dfn*x + dfd)
    """
    if x <= 0:
        return 0.0
    y = dfn * x / (dfn * x + dfd)
    lam = nc / 2.0
    jmax = int(lam + 12.0 * math.sqrt(lam) + 60)
    j = np.arange(0, jmax + 1)
    w = stats.poisson.pmf(j, lam)
    b = special.betainc(dfn / 2.0 + j, dfd / 2.0, y)
    return _clip01(float(np.sum(w * b)))


def ncf_cdf(x: float, dfn: int, dfd: int, nc: float) -> float:
    """Merkezsel olmayan F CDF'i: ncfdtr -> ncf.cdf -> Poisson karışımı."""
    for fn in (lambda: float(special.ncfdtr(dfn, dfd, nc, x)), lambda: float(stats.ncf.cdf(x, dfn, dfd, nc))):
        try:
            v = fn()
        except Exception:
            continue
        if math.isfinite(v):
            return _clip01(v)
    v = ncf_cdf_poisson(x, dfn, dfd, nc)
    if not math.isfinite(v):
        raise InputError("güç hesabı sayısal olarak çözülemedi")
    return v
