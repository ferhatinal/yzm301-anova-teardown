"""MCP katmanı: (1) CLI ile aynı girdide aynı çıktı, (2) araç şeması, (3) hesap kopyalanmadı.

Ödev: "CLI ile MCP'nin aynı girdide aynı çıktıyı verdiğini gösteren testler."
"""

import asyncio
import inspect
import json
import os
import subprocess
import sys
import unittest

import _path  # noqa: F401
from powerlab import mcp_server, tools

ENV = {**os.environ, "PYTHONPATH": _path.SRC}

A_PRIORI = [  # (f, alpha, power, groups): geçerli ve geçersiz girdiler
    (0.25, 0.05, 0.95, 3), (0.25, 0.05, 0.80, 3), (0.10, 0.05, 0.80, 3), (0.40, 0.01, 0.90, 4),
    (0.25, 0.10, 0.99, 2), (5.0, 0.05, 0.80, 3),          # çok büyük f -> alt sınır
    (0.0, 0.05, 0.90, 3), (0.25, 0.05, 0.05, 3), (0.25, 0.05, 0.90, 1), (0.25, 1.0, 0.90, 3),  # hata dalları
]
POST_HOC = [(0.25, 0.05, 3, 159), (0.4, 0.01, 4, 80), (0.25, 0.05, 3, 3), (0.0, 0.05, 3, 100)]


def cli_json(*args):
    p = subprocess.run([sys.executable, "-m", "powerlab", *args], capture_output=True, text=True, env=ENV)
    return json.loads(p.stdout)


def mcp_json(name, args):
    server = mcp_server.build_server()
    res = asyncio.run(server.call_tool(name, args))
    assert not res.is_error, res
    return json.loads(res.content[0].text)


class Parity(unittest.TestCase):
    def test_a_priori_cli_equals_mcp(self):
        for f, a, p, k in A_PRIORI:
            c = cli_json("--test", "anova-oneway", "--mode", "a-priori", "--f", str(f), "--alpha", str(a),
                         "--power", str(p), "--groups", str(k))
            m = mcp_json("anova_oneway_a_priori", {"f": f, "alpha": a, "power": p, "groups": k})
            self.assertEqual(c, m, (f, a, p, k))

    def test_post_hoc_cli_equals_mcp(self):
        for f, a, k, n in POST_HOC:
            c = cli_json("--test", "anova-oneway", "--mode", "post-hoc", "--f", str(f), "--alpha", str(a),
                         "--groups", str(k), "--n-total", str(n))
            m = mcp_json("anova_oneway_post_hoc", {"f": f, "alpha": a, "groups": k, "n_total": n})
            self.assertEqual(c, m, (f, a, k, n))


class Schema(unittest.TestCase):
    def test_server_lists_exactly_the_registered_tools(self):
        names = {t.name for t in asyncio.run(mcp_server.build_server().list_tools())}
        self.assertEqual(names, set(tools.TOOLS))

    def test_required_fields_match_registry(self):
        for t in asyncio.run(mcp_server.build_server().list_tools()):
            schema = getattr(t, "input_schema", None) or getattr(t, "inputSchema")
            self.assertEqual(set(schema["required"]), set(tools.TOOLS[t.name]["input_schema"]["required"]), t.name)

    def test_unknown_tool_is_error_dict_not_exception(self):
        self.assertIn("error", tools.call("nope", {}))


class NoLogicInAdapter(unittest.TestCase):
    """Hesap mantığı MCP katmanına kopyalanmadı: adaptör kaynağında dağılım/arama kodu yok."""

    def test_adapter_sources_have_no_numeric_code(self):
        for mod in (mcp_server, tools):
            src = inspect.getsource(mod)
            for banned in ("scipy", "stats.f", "ncf", "ppf", "math.ceil", "numpy"):
                self.assertNotIn(banned, src, (mod.__name__, banned))


if __name__ == "__main__":
    unittest.main()
