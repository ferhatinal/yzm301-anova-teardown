"""REFERANS aile (t2-indep): ödev sözleşmesindeki örnek ve scipy NaN regresyonu.
Teslimden önce t2_indep ile birlikte silinebilir."""

import math
import unittest

import _path  # noqa: F401
from powerlab.errors import InputError
from powerlab.families import t2_indep as T


class T2Reference(unittest.TestCase):
    def test_documented_example(self):
        r = T.a_priori(2, 0.5, 0.05, 0.95, 1.0)
        self.assertEqual((r.n1, r.n2), (105, 105))

    def test_nan_regression_df254(self):
        """HALLUCINATIONS.md H-A: scipy nct.cdf(x<0) bazı girdilerde NaN verir."""
        p = T.t2_power(2, 0.8, 0.01, 128, 128)[0]
        self.assertTrue(math.isfinite(p))
        self.assertAlmostEqual(p, 0.99992225, places=7)  # bağımsız quad doğrulaması

    def test_a_priori_no_longer_overshoots(self):
        self.assertEqual(T.a_priori(2, 0.8, 0.01, 0.99, 1.0).n1, 77)  # statsmodels: 76.78

    def test_d_zero_rejected(self):
        with self.assertRaises(InputError):
            T.a_priori(2, 0.0, 0.05, 0.95)


if __name__ == "__main__":
    unittest.main()
