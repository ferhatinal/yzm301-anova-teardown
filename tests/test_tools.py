"""tools/add_oracle_row.py düzenek testi. Sentetik değerler kullanır ve GERÇEK oracle CSV'sine yazmaz.

Bu değerler G*Power'dan gelmez; yalnızca betiğin sütunları doğru yazdığını ve motorla
karşılaştırmayı doğru yaptığını sınar.
"""

import csv
import importlib.util
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

import _path  # noqa: F401
from powerlab import tools

SPEC = importlib.util.spec_from_file_location("add_oracle_row", os.path.join(_path.ROOT, "tools", "add_oracle_row.py"))
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def run(argv, path):
    mod.PATH = path
    old = sys.argv
    sys.argv = ["add_oracle_row.py", *argv]
    buf = StringIO()
    try:
        with redirect_stdout(buf):
            code = mod.main()
    finally:
        sys.argv = old
    return code, buf.getvalue()


class AddOracleRow(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "o.csv")

    def tearDown(self):
        self.dir.cleanup()

    def test_matching_row_is_written_with_header_and_reported_compatible(self):
        r = tools.call("anova_oneway_a_priori", {"f": 0.25, "alpha": 0.05, "power": 0.8, "groups": 3})
        code, out = run(["a-priori", "--f", "0.25", "--alpha", "0.05", "--power", "0.8", "--groups", "3",
                         "--n-total", str(r["n_total"]), "--df1", str(r["df1"]), "--df2", str(r["df2"]),
                         "--actual-power", str(r["actual_power"]), "--critical", str(r["critical"]),
                         "--ncp", str(r["ncp"]), "--no-screenshot-check"], self.path)
        self.assertEqual(code, 0, out)
        with open(self.path, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(list(rows[0].keys()), mod.HEADER)
        self.assertEqual(rows[0]["n_per_group"], str(r["n_total"] // 3))
        self.assertEqual(rows[0]["source"], "gpower-3.1.9.7-gui")

    def test_mismatching_row_is_flagged(self):
        r = tools.call("anova_oneway_a_priori", {"f": 0.25, "alpha": 0.05, "power": 0.8, "groups": 3})
        code, out = run(["a-priori", "--f", "0.25", "--alpha", "0.05", "--power", "0.8", "--groups", "3",
                         "--n-total", str(r["n_total"] - 1), "--df1", "2", "--df2", str(r["df2"]),
                         "--actual-power", str(r["actual_power"]), "--critical", str(r["critical"]),
                         "--ncp", str(r["ncp"]), "--no-screenshot-check"], self.path)
        self.assertEqual(code, 1)
        self.assertIn("UYUŞMUYOR", out)

    def test_expect_error_row_matches_engine_error(self):
        code, out = run(["a-priori", "--f", "0", "--alpha", "0.05", "--power", "0.8", "--groups", "3",
                         "--expect-error", "--note", "sentetik", "--no-screenshot-check"], self.path)
        self.assertEqual(code, 0, out)

    def test_post_hoc_row_roundtrip(self):
        r = tools.call("anova_oneway_post_hoc", {"f": 0.25, "alpha": 0.05, "groups": 3, "n_total": 90})
        code, out = run(["post-hoc", "--f", "0.25", "--alpha", "0.05", "--groups", "3", "--n-total", "90",
                         "--df1", str(r["df1"]), "--df2", str(r["df2"]), "--actual-power", str(r["actual_power"]),
                         "--critical", str(r["critical"]), "--ncp", str(r["ncp"]), "--no-screenshot-check"], self.path)
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
