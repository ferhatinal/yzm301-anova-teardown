import unittest

from anova_clean import a_priori, post_hoc, _power, _ncf_cdf_series
from scipy import stats


class TestScenarios(unittest.TestCase):
    def test_apriori_multiple_of_k(self):
        r = a_priori(0.25, 0.05, 0.80, 3)
        self.assertEqual(r["n_total"] % 3, 0)
        self.assertGreaterEqual(r["actual_power"], 0.80)
        prev = _power(0.25, 0.05, 3, r["n_total"] - 3)["actual_power"]
        self.assertLess(prev, 0.80)

    def test_manual_example(self):
        r = a_priori(0.25, 0.05, 0.95, 10)
        self.assertEqual(r["n_total"], 390)
        self.assertAlmostEqual(r["actual_power"], 0.952363, places=6)
        self.assertAlmostEqual(r["critical"], 1.904538, places=6)
        self.assertEqual(r["df1"], 9)
        self.assertEqual(r["df2"], 380)
        self.assertAlmostEqual(r["ncp"], 24.375, places=9)

    def test_min_n_is_2k(self):
        self.assertEqual(a_priori(50, 0.05, 0.80, 4)["n_total"], 8)

    def test_posthoc_non_multiple(self):
        r = post_hoc(0.25, 0.05, 3, 100)
        self.assertEqual(r["df1"], 2)
        self.assertEqual(r["df2"], 97)
        self.assertAlmostEqual(r["ncp"], 6.25, places=9)
        self.assertTrue(0 < r["actual_power"] < 1)

    def test_posthoc_f0_power_equals_alpha(self):
        self.assertAlmostEqual(post_hoc(0, 0.05, 3, 30)["actual_power"], 0.05, places=12)

    def test_power_equals_alpha_valid(self):
        self.assertEqual(a_priori(0.25, 0.05, 0.05, 3)["n_total"], 6)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): a_priori(0.25, 0.05, 0.8, 1)
        with self.assertRaises(ValueError): post_hoc(0.25, 0.05, 1, 30)
        with self.assertRaises(ValueError): post_hoc(0.25, 0.05, 3, 3)
        with self.assertRaises(ValueError): a_priori(0.25, 0.05, 0.04, 3)
        with self.assertRaises(ValueError): a_priori(0, 0.05, 0.8, 3)
        with self.assertRaises(ValueError): a_priori(51, 0.05, 0.8, 3)
        with self.assertRaises(ValueError): a_priori(0.25, 0, 0.8, 3)
        with self.assertRaises(ValueError): a_priori(0.25, 1, 0.8, 3)


class TestBoundaries(unittest.TestCase):
    def test_f_bounds(self):
        a_priori(1e-6 * 1.0 + 1e-3, 0.05, 0.8, 3)  # sanity, not extreme
        a_priori(50, 0.05, 0.8, 3)
        with self.assertRaises(ValueError): a_priori(1e-7, 0.05, 0.8, 3)
        post_hoc(0, 0.05, 3, 4)
        post_hoc(50, 0.05, 3, 4)
        with self.assertRaises(ValueError): post_hoc(-0.01, 0.05, 3, 30)
        with self.assertRaises(ValueError): post_hoc(50.01, 0.05, 3, 30)

    def test_alpha_power_bounds(self):
        a_priori(0.5, 1e-7, 0.8, 3)
        a_priori(0.5, 0.05, 0.9999999, 3)
        a_priori(0.5, 0.9999999, 0.9999999, 3)
        with self.assertRaises(ValueError): a_priori(0.5, 0.05, 1.0, 3)
        with self.assertRaises(ValueError): a_priori(0.5, 0.05, 0.0, 3)
        with self.assertRaises(ValueError): a_priori(0.5, 0.05, 0.9999999 + 1e-9, 3)
        with self.assertRaises(ValueError): a_priori(0.5, 1e-8, 0.8, 3)

    def test_n_bounds(self):
        post_hoc(0.25, 0.05, 3, 4)  # k < N strict
        with self.assertRaises(ValueError): post_hoc(0.25, 0.05, 3, 2)
        with self.assertRaises(ValueError): post_hoc(0.25, 0.05, 3, 30.5)

    def test_k_bounds(self):
        a_priori(0.25, 0.05, 0.8, 2)
        with self.assertRaises(ValueError): a_priori(0.25, 0.05, 0.8, 0)
        with self.assertRaises(ValueError): a_priori(0.25, 0.05, 0.8, 2.5)

    def test_minimality_property(self):
        for f, p, k in [(0.1, 0.8, 4), (0.4, 0.9, 5), (0.25, 0.8, 2)]:
            r = a_priori(f, 0.05, p, k)
            self.assertGreaterEqual(r["actual_power"], p)
            if r["n_total"] > 2 * k:
                self.assertLess(_power(f, 0.05, k, r["n_total"] - k)["actual_power"], p)

    def test_fallback_series_matches_scipy(self):
        crit = stats.f.ppf(0.95, 9, 380)
        ref = stats.ncf.cdf(crit, 9, 380, 24.375)
        self.assertAlmostEqual(_ncf_cdf_series(crit, 9, 380, 24.375), ref, places=9)


if __name__ == "__main__":
    unittest.main()
