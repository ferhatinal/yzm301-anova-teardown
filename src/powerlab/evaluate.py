"""Ajan değerlendirmesi: 10 soruluk setle araç seçimi, parametre ve N doğruluğu.

Ölçülen:
  tool_ok    : doğru araç seçildi mi (desteklenmeyen/belirsiz sorularda hiç araç çağrılmamalı)
  params_ok  : araç argümanları beklenenle aynı mı (soru -> parametre çıkarımı)
  n_ok       : a priori N, G*Power kâhin değeriyle aynı mı (yalnızca expected_n_total doluysa)
  power_ok   : post hoc güç, G*Power kâhin değeriyle aynı mı (yalnızca expected_power doluysa)
Kâhin alanları boşsa ilgili metrik "ölçülmedi" sayılır; uydurma değer kullanılmaz.
"""

from __future__ import annotations

import json
import math


def load_questions(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _args_equal(got: dict, exp: dict) -> bool:
    if set(got) != set(exp):
        return False
    for k, v in exp.items():
        g = got[k]
        if isinstance(v, float) or isinstance(g, float):
            if not math.isclose(float(g), float(v), rel_tol=0, abs_tol=1e-9):
                return False
        elif g != v:
            return False
    return True


def score(question: dict, tool_calls: list[dict]) -> dict:
    """Tek soru için puan. `tool_calls`: [{"name","arguments","result"}, ...]."""
    exp_tool = question.get("expected_tool")
    out = {"id": question["id"], "tool_ok": None, "params_ok": None, "n_ok": None, "power_ok": None,
           "called": [c["name"] for c in tool_calls]}
    if exp_tool is None:
        out["tool_ok"] = len(tool_calls) == 0
        return out
    last = tool_calls[-1] if tool_calls else None
    out["tool_ok"] = bool(last) and last["name"] == exp_tool
    if out["tool_ok"]:
        out["params_ok"] = _args_equal(last["arguments"], question["expected_params"])
        res = last["result"]
        if question.get("expected_n_total") is not None:
            out["n_ok"] = res.get("n_total") == question["expected_n_total"]
        if question.get("expected_power") is not None:
            out["power_ok"] = res.get("actual_power") == round(float(question["expected_power"]), 4)
    else:
        out["params_ok"] = False
    return out


def summarize(scores: list[dict], usage: list[dict] | None = None) -> dict:
    def rate(key):
        vals = [s[key] for s in scores if s[key] is not None]
        return {"dogru": sum(vals), "olculen": len(vals),
                "oran": round(sum(vals) / len(vals), 3) if vals else None}
    summary = {"soru_sayisi": len(scores), "arac_secimi": rate("tool_ok"), "parametreler": rate("params_ok"),
               "N_tam_eslesme": rate("n_ok"), "guc_eslesme": rate("power_ok")}
    if usage:
        summary["toplam_girdi_token"] = sum(u.get("input_tokens", 0) for u in usage)
        summary["toplam_cikti_token"] = sum(u.get("output_tokens", 0) for u in usage)
        summary["toplam_sure_sn"] = round(sum(u.get("seconds", 0) for u in usage), 2)
    return summary
