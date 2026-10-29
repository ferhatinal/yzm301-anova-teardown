"""F testi, tek yönlü ANOVA: birim, bölüm (eşdeğerlik) ve sınır değer testleri.

Beklenen değerler teori/scipy'den gelir ([DOK]); G*Power eşleşmesi ayrı katman:
tests/differential.py + oracle/*.csv. HIPOTEZ testleri adında hXX taşır; kâhin
(G*Power) farklı çıkarsa o test DEĞİL motor güncellenir.
"""

import math
import unittest

import _path  # noqa: F401
from powerlab import robust
from powerlab.errors import InputError
from powerlab.families import anova_oneway as A


class PowerFunction(unittest.TestCase):
    def test_df_and_ncp_formulas(self):
        _, _, df1, df2, ncp = A.anova_power(0.25, 0.05, 3, 159)
        self.assertEqual((df1, df2), (2, 156))
        self.assertAlmostEqual(ncp, 0.25 ** 2 * 159, places=12)

    def test_critical_f_matches_scipy(self):
        from scipy import stats
        _, crit, df1, df2, _ = A.anova_power(0.25, 0.05, 3, 159)
        self.assertAlmostEqual(crit, stats.f.ppf(0.95, df1, df2), places=12)

    def test_power_monotone_in_n(self):
        prev = 0.0
        for n in range(6, 600, 6):
            p = A.anova_power(0.25, 0.05, 3, n)[0]
            self.assertGreaterEqual(p, prev)
            prev = p

    def test_power_monotone_in_f(self):
        prev = 0.0
        for f in (0.05, 0.1, 0.25, 0.4, 0.8):
            p = A.anova_power(f, 0.05, 3, 90)[0]
            self.assertGreater(p, prev)
            prev = p

    def test_more_groups_same_n_total_less_power_at_fixed_f(self):
        # sabit f ve N'de df1 büyüdükçe güç düşer
        self.assertGreater(A.anova_power(0.25, 0.05, 3, 120)[0], A.anova_power(0.25, 0.05, 6, 120)[0])

    def test_poisson_mixture_agrees_with_scipy_path(self):
        from scipy import stats
        crit = stats.f.ppf(0.95, 2, 156)
        a = robust.ncf_cdf(crit, 2, 156, 9.9375)
        b = robust.ncf_cdf_poisson(crit, 2, 156, 9.9375)
        self.assertAlmostEqual(a, b, places=9)

    def test_power_finite_over_grid_and_two_independent_paths_agree(self):
        from scipy import stats
        for k in (2, 3, 5):
            for n_per in (3, 10, 50, 200, 1000):
                for f in (0.05, 0.25, 0.8):
                    n = k * n_per
                    df1, df2, nc = k - 1, n - k, f * f * n
                    crit = stats.f.ppf(0.95, df1, df2)
                    p1 = 1 - robust.ncf_cdf(crit, df1, df2, nc)
                    p2 = 1 - robust.ncf_cdf_poisson(crit, df1, df2, nc)
                    self.assertTrue(math.isfinite(p1), (k, n, f))
                    self.assertAlmostEqual(p1, p2, places=7, msg=(k, n, f))


class APriori(unittest.TestCase):
    def test_textbook_values_sanity(self):
        # f=0.25, alpha=.05, k=3: yaygın ders kitabı değerleri (kâhin DEĞİL, sağduyu kontrolü)
        self.assertEqual(A.a_priori(0.25, 0.05, 0.80, 3).n_total, 159)
        self.assertEqual(A.a_priori(0.25, 0.05, 0.95, 3).n_total, 252)

    def test_minimality_in_group_units(self):
        for f, pw in ((0.1, 0.8), (0.25, 0.9), (0.4, 0.95)):
            r = A.a_priori(f, 0.05, pw, 3)
            self.assertGreaterEqual(r.actual_power, pw)
            below = A.anova_power(f, 0.05, 3, r.n_total - 3)[0]
            self.assertLess(below, pw)

    def test_h07_total_is_multiple_of_groups(self):
        for k in (2, 3, 4, 5):
            self.assertEqual(A.a_priori(0.3, 0.05, 0.9, k).n_total % k, 0)

    def test_a_priori_is_smallest_multiple_of_k_via_independent_search(self):
        """Bagimsiz kaba kuvvet: ilk saglayan N'yi bul, k'nin katina yuvarla (R27)."""
        for f, pw, k in ((0.25, 0.80, 3), (0.25, 0.95, 3), (0.25, 0.95, 4), (0.4, 0.9, 5)):
            first = next(n for n in range(k + 1, 100000) if A.anova_power(f, 0.05, k, n)[0] >= pw)
            self.assertEqual(A.a_priori(f, 0.05, pw, k).n_total, k * math.ceil(first / k))

    def test_post_hoc_matches_a_priori_actual_power(self):
        a = A.a_priori(0.25, 0.05, 0.95, 3)
        b = A.post_hoc(0.25, 0.05, 3, a.n_total)
        self.assertAlmostEqual(a.actual_power, b.actual_power, places=12)


class ManualExample(unittest.TestCase):
    """[DOK] G*Power 3.1 kılavuzu (Haziran 2023), Bölüm 10, Örnek 10.3: kılavuzun BASILI çıktısı.

    Kâhin G*Power ekranı değil, kılavuzdaki sayılardır (6 basamak). Bu örnek H-07 için bağımsız
    kanıttır: birer-artış arama 386 verir, kılavuz 390 verir.
    """

    def test_a_priori_matches_printed_output_to_six_digits(self):
        r = A.a_priori(0.25, 0.05, 0.95, 10)
        self.assertEqual(r.n_total, 390)
        self.assertEqual(r.n_total // 10, 39)             # kılavuz: "39 subjects in each of the 10 groups"
        self.assertEqual((r.df1, r.df2), (9, 380))
        self.assertEqual(round(r.actual_power, 6), 0.952363)
        self.assertEqual(round(r.critical, 6), 1.904538)
        self.assertEqual(round(r.ncp, 6), 24.375)

    def test_unit_step_search_would_have_given_386_not_390(self):
        first = next(n for n in range(11, 10000) if A.anova_power(0.25, 0.05, 10, n)[0] >= 0.95)
        self.assertEqual(first, 386)
        self.assertEqual(A.a_priori(0.25, 0.05, 0.95, 10).n_total, 390)

    def test_compromise_example_cross_check_with_printed_alpha(self):
        # Kılavuzun compromise çıktısı: alpha=0.159194, N=200, k=10 -> güç 0.840806, F* 1.476210
        r = A.post_hoc(0.25, 0.159194, 10, 200)
        self.assertAlmostEqual(r.actual_power, 0.840806, places=5)   # alpha 6 basamağa yuvarlı
        self.assertAlmostEqual(r.critical, 1.476210, places=5)
        self.assertEqual((r.df1, r.df2), (9, 190))
        self.assertEqual(round(r.ncp, 6), 12.5)


class Boundaries(unittest.TestCase):
    """Bölüm testi sınıfları (Sommerville 8.1.2): dejenere, çok küçük, Cohen eşikleri, çok büyük."""

    def test_f_zero_and_negative_rejected(self):
        for f in (0.0, -0.1, float("nan"), float("inf")):
            with self.assertRaises(InputError):
                A.a_priori(f, 0.05, 0.9, 3)

    def test_tiny_f_gives_large_n(self):
        self.assertGreater(A.a_priori(0.02, 0.05, 0.8, 3).n_total, 20000)

    def test_cohen_thresholds_ordering(self):
        small, medium, large = (A.a_priori(f, 0.05, 0.8, 3).n_total for f in (0.1, 0.25, 0.4))
        self.assertGreater(small, medium)
        self.assertGreater(medium, large)

    def test_huge_f_hits_lower_bound_h03(self):
        r = A.a_priori(5.0, 0.05, 0.8, 3)
        self.assertEqual(r.n_total, 3 * A.MIN_PER_GROUP)

    def test_groups_validation_h08(self):
        for k in (1, 0, -3):
            with self.assertRaises(InputError):
                A.a_priori(0.25, 0.05, 0.9, k)
        with self.assertRaises(InputError):
            A.a_priori(0.25, 0.05, 0.9, 3.0)  # tam sayı olmalı

    def test_alpha_and_power_range(self):
        for a in (0, 1, -0.1, 1.2):
            with self.assertRaises(InputError):
                A.a_priori(0.25, a, 0.9, 3)
        for p in (0, 1, -0.2, 1.5):
            with self.assertRaises(InputError):
                A.a_priori(0.25, 0.05, p, 3)

    def test_power_below_alpha_rejected_r6(self):
        for p in (0.04, 0.01):
            with self.assertRaises(InputError):
                A.a_priori(0.25, 0.05, p, 3)

    def test_power_equal_alpha_valid_r6(self):  # [REA] R6: esitlik gecerli
        self.assertEqual(A.a_priori(0.25, 0.05, 0.05, 3).n_total, 6)

    def test_bounds_r30_r36(self):
        for args in ((0.25, 0.0, 0.8, 3), (0.25, 1.0, 0.99, 3), (51, 0.05, 0.8, 3), (0, 0.05, 0.8, 3)):
            with self.assertRaises(InputError):
                A.a_priori(*args)
        self.assertAlmostEqual(A.post_hoc(0, 0.05, 3, 30).actual_power, 0.05, places=6)

    def test_post_hoc_n_total_must_exceed_groups(self):
        for n in (3, 2, 0, -5):
            with self.assertRaises(InputError):
                A.post_hoc(0.25, 0.05, 3, n)

    def test_unreachable_n_is_error_not_hang(self):
        with self.assertRaises(InputError):
            A.a_priori(1e-6, 0.05, 0.9999999, 3)


if __name__ == "__main__":
    unittest.main()
