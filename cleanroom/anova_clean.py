"""One-way fixed-effects ANOVA (omnibus) power analysis, per SPEC.md."""
import math
import numbers

from scipy import special, stats

_LAMBDA_MIN = 1e-10
_MAX_MULT = 10 ** 12  # safety cap on N/k during search


def _is_int(x):
    return isinstance(x, numbers.Integral) and not isinstance(x, bool) or (
        isinstance(x, float) and math.isfinite(x) and x == int(x))


def _check_num(name, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, numbers.Real):
        raise ValueError(f"{name} must be a number")
    v = float(v)
    if not math.isfinite(v) or v < lo or v > hi:
        raise ValueError(f"{name} is outside the admissible range ({lo:g}, {hi:g})")
    return v


def _check_k(k):
    if not _is_int(k) or int(k) < 2:
        raise ValueError("There must be at least 2 groups.")
    return int(k)


def _ncf_cdf_series(x, df1, df2, lam):
    """Poisson-weighted incomplete-beta series (cumfnc-like) fallback."""
    if x <= 0:
        return 0.0
    xnonc = lam / 2.0
    y = df1 * x / (df2 + df1 * x)
    # start at the Poisson mode and sum outward in both directions
    m = int(math.floor(xnonc))
    total = 0.0
    log_x = math.log(xnonc) if xnonc > 0 else 0.0

    def term(i):
        w = math.exp(-xnonc + i * log_x - math.lgamma(i + 1)) if xnonc > 0 else (1.0 if i == 0 else 0.0)
        return w * special.betainc(df1 / 2.0 + i, df2 / 2.0, y)

    i = m
    while i >= 0:
        t = term(i)
        total += t
        if t < 1e-20 * max(total, 1e-300) and i < m:
            break
        i -= 1
    i = m + 1
    while True:
        t = term(i)
        total += t
        if t < 1e-13 * max(total, 1e-300) and i > m + 1:
            break
        if i > m + 100000:
            break
        i += 1
    return min(total, 1.0)


def _power(f, alpha, k, n):
    """Power for (real) total sample size n; returns dict of pieces."""
    df1 = k - 1
    df2 = n - k
    lam = f * f * n
    crit = float(stats.f.ppf(1.0 - alpha, df1, df2))
    if lam < _LAMBDA_MIN:
        pw = float(stats.f.sf(crit, df1, df2))
    else:
        try:
            with _quiet():
                p = float(stats.ncf.sf(crit, df1, df2, lam))
        except Exception:
            p = float("nan")
        if not math.isfinite(p):
            p = 1.0 - _ncf_cdf_series(crit, df1, df2, lam)
        pw = min(max(p, 0.0), 1.0)
    return {"actual_power": pw, "critical": crit, "df1": df1, "df2": df2, "ncp": lam}


class _quiet:
    def __enter__(self):
        import warnings
        self._w = warnings.catch_warnings()
        self._w.__enter__()
        warnings.simplefilter("ignore")

    def __exit__(self, *a):
        return self._w.__exit__(*a)


def _result(f, alpha, k, n):
    r = _power(f, alpha, k, n)
    return {"n_total": n, **r}


def a_priori(f, alpha, power, groups):
    k = _check_k(groups)
    f = _check_num("Effect size f", f, 1e-6, 50.0)
    alpha = _check_num("Alpha", alpha, 1e-7, 0.9999999)
    power = _check_num("Power", power, 1e-7, 0.9999999)
    if alpha > power:
        raise ValueError("Power must be greater than or equal to alpha.")

    def ok(m):
        return _power(f, alpha, k, m * k)["actual_power"] >= power

    lo = 2  # smallest allowed: N = 2k
    if ok(lo):
        m = lo
    else:
        hi = lo * 2
        while not ok(hi):
            lo = hi
            hi *= 2
            if hi > _MAX_MULT:
                raise ValueError("Sample size could not be computed (too large).")
        # invariant: not ok(lo), ok(hi)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid
        m = hi
    return _result(f, alpha, k, m * k)


def post_hoc(f, alpha, groups, n_total):
    k = _check_k(groups)
    f = _check_num("Effect size f", f, 0.0, 50.0)
    alpha = _check_num("Alpha", alpha, 1e-7, 0.9999999)
    if not _is_int(n_total) or int(n_total) <= k:
        raise ValueError("Sample size must be greater than the number of groups (k)")
    return _result(f, alpha, k, int(n_total))
