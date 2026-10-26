"""CLI sözleşme testleri: tek satır JSON, hata biçimi, çıkış kodları.

NOT: ANOVA çıktı alan adları (n_per_group, n_total, actual_power, critical, df1, df2, ncp)
CONTRACT.md elimize geçene kadar VARSAYIMDIR. Resmi alan adları farklıysa yalnızca
AnovaResult.as_contract_dict() ve bu dosyadaki ANOVA_KEYS güncellenir.
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = {**os.environ, "PYTHONPATH": os.path.join(ROOT, "src")}
ANOVA_KEYS = ["n_per_group", "n_total", "actual_power", "critical", "df1", "df2", "ncp"]


def cli(*args):
    p = subprocess.run([sys.executable, "-m", "powerlab", *args], capture_output=True, text=True, env=ENV)
    return p.returncode, p.stdout


class SuccessShape(unittest.TestCase):
    def test_anova_single_line_json_with_expected_keys(self):
        code, out = cli("--test", "anova-oneway", "--mode", "a-priori", "--f", "0.25",
                        "--groups", "3", "--alpha", "0.05", "--power", "0.95")
        self.assertEqual(code, 0)
        self.assertEqual(out.count("\n"), 1)
        obj = json.loads(out)
        self.assertEqual(list(obj.keys()), ANOVA_KEYS)
        self.assertEqual(obj["n_total"] % 3, 0)
        self.assertGreaterEqual(obj["actual_power"], 0.95)

    def test_anova_post_hoc(self):
        code, out = cli("--test", "anova-oneway", "--mode", "post-hoc", "--f", "0.25",
                        "--groups", "3", "--alpha", "0.05", "--n-total", "159")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["n_total"], 159)

    def test_documented_t2_example_exact_line(self):
        """Ödev metnindeki sözleşme örneği ([DOK]): biçim regresyonu."""
        code, out = cli("--test", "t2-indep", "--mode", "a-priori", "--tails", "2", "--d", "0.5",
                        "--alpha", "0.05", "--power", "0.95", "--ratio", "1")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), '{"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,'
                                      '"critical":1.9714,"df":208,"ncp":3.6228}')


class ErrorContract(unittest.TestCase):
    def assert_error(self, expected_code_nonzero, *args):
        code, out = cli(*args)
        self.assertNotEqual(code, 0)
        if expected_code_nonzero:
            self.assertEqual(code, expected_code_nonzero)
        obj = json.loads(out)
        self.assertEqual(list(obj.keys()), ["error"])
        self.assertTrue(obj["error"])

    base = ("--test", "anova-oneway", "--mode", "a-priori")

    def test_f_zero(self):
        self.assert_error(2, *self.base, "--f", "0", "--groups", "3", "--alpha", "0.05", "--power", "0.9")

    def test_groups_one(self):
        self.assert_error(2, *self.base, "--f", "0.25", "--groups", "1", "--alpha", "0.05", "--power", "0.9")

    def test_missing_param(self):
        self.assert_error(2, *self.base, "--f", "0.25", "--alpha", "0.05", "--power", "0.9")

    def test_foreign_param(self):
        self.assert_error(2, *self.base, "--d", "0.5", "--f", "0.25", "--groups", "3", "--alpha", "0.05", "--power", "0.9")

    def test_power_below_alpha(self):
        self.assert_error(2, *self.base, "--f", "0.25", "--groups", "3", "--alpha", "0.05", "--power", "0.04")

    def test_unknown_family(self):
        self.assert_error(3, "--test", "nope", "--mode", "a-priori")

    def test_unknown_mode_is_json_error(self):
        self.assert_error(2, "--test", "anova-oneway", "--mode", "bogus")

    def test_non_numeric_value_is_json_error(self):
        self.assert_error(2, *self.base, "--f", "abc", "--groups", "3", "--alpha", "0.05", "--power", "0.9")


if __name__ == "__main__":
    unittest.main()
