"""Ajan döngüsü ve değerlendirici testleri (SAHTE istemci; gerçek model doğruluğu ölçülmez).

Bu testler şunları doğrular: araç kullanım döngüsü, sayıların yalnızca motordan gelmesi,
hata aktarımı, tur sınırı, log biçimi ve puanlama mantığı. "Gerçek modelin doğru aracı seçme
oranı" ancak `eval/run_eval.py --live` ile ölçülür.
"""

import json
import os
import tempfile
import types
import unittest

import _path  # noqa: F401
from powerlab import agent, evaluate, tools

QUESTIONS = evaluate.load_questions(os.path.join(_path.ROOT, "eval", "questions.jsonl"))


def block(type_, **kw):
    return types.SimpleNamespace(type=type_, **kw)


def response(*blocks, tokens=(100, 20)):
    return types.SimpleNamespace(content=list(blocks),
                                 usage=types.SimpleNamespace(input_tokens=tokens[0], output_tokens=tokens[1]))


class ScriptedClient:
    """Soru metnine göre önceden yazılmış davranış: ilk tur araç çağrısı, ikinci tur metin."""

    def __init__(self, script):
        self.script = script           # question -> ("tool", name, args) | ("text", yazı)
        self.messages = types.SimpleNamespace(create=self._create)
        self.calls = 0

    def _create(self, model, max_tokens, system, tools, messages):
        self.calls += 1
        question = messages[0]["content"]
        kind = self.script[question]
        last = messages[-1]
        if kind[0] == "text":
            return response(block("text", text=kind[1]))
        if last["role"] == "user" and isinstance(last["content"], list):      # araç sonucu geldi
            payload = json.loads(last["content"][0]["content"])
            return response(block("text", text="Sonuç: " + json.dumps(payload, ensure_ascii=False)))
        return response(block("tool_use", id=f"tu_{self.calls}", name=kind[1], input=kind[2]))


def perfect_script():
    s = {}
    for q in QUESTIONS:
        if q["expected_tool"] is None:
            s[q["question"]] = ("text", "Bu soruyu bu araçla yanıtlayamam; ayrıntı lütfen.")
        else:
            s[q["question"]] = ("tool", q["expected_tool"], dict(q["expected_params"]))
    return s


class AgentLoop(unittest.TestCase):
    def test_numbers_come_from_engine_not_from_model(self):
        q = QUESTIONS[0]
        res = agent.run_question(ScriptedClient(perfect_script()), q["question"])
        self.assertEqual(len(res.tool_calls), 1)
        engine_out = tools.call("anova_oneway_a_priori", q["expected_params"])
        self.assertEqual(res.tool_calls[0]["result"], engine_out)
        self.assertIn(str(engine_out["n_total"]), res.answer)

    def test_token_and_turn_accounting(self):
        res = agent.run_question(ScriptedClient(perfect_script()), QUESTIONS[0]["question"])
        self.assertEqual(res.turns, 2)
        self.assertEqual((res.input_tokens, res.output_tokens), (200, 40))

    def test_no_tool_for_unsupported_question(self):
        res = agent.run_question(ScriptedClient(perfect_script()), QUESTIONS[6]["question"])
        self.assertEqual(res.tool_calls, [])
        self.assertTrue(res.answer)

    def test_tool_error_is_passed_through_not_invented(self):
        script = {"x": ("tool", "anova_oneway_a_priori", {"f": 0, "alpha": 0.05, "power": 0.8, "groups": 3})}
        res = agent.run_question(ScriptedClient(script), "x")
        self.assertIn("error", res.tool_calls[0]["result"])
        self.assertIn("error", res.answer)

    def test_unknown_tool_does_not_crash(self):
        res = agent.run_question(ScriptedClient({"x": ("tool", "nope", {})}), "x")
        self.assertIn("error", res.tool_calls[0]["result"])

    def test_turn_limit(self):
        class Loop:
            messages = types.SimpleNamespace(create=lambda **kw: response(
                block("tool_use", id="t", name="anova_oneway_post_hoc",
                      input={"f": 0.25, "alpha": 0.05, "groups": 3, "n_total": 90})))
        res = agent.run_question(Loop(), "x", max_turns=3)
        self.assertEqual(res.turns, 3)
        self.assertIn("sınır", res.answer)

    def test_log_is_valid_jsonl(self):
        res = agent.run_question(ScriptedClient(perfect_script()), QUESTIONS[2]["question"])
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "calls.jsonl")
            agent.log_result(res, path)
            agent.log_result(res, path)
            with open(path, encoding="utf-8") as fh:
                rows = [json.loads(line) for line in fh]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["tool_calls"][0]["name"], "anova_oneway_post_hoc")

    def test_system_prompt_forbids_self_computation_and_unsupported_families(self):
        self.assertIn("ASLA kendin hesaplama", agent.SYSTEM_PROMPT)
        self.assertIn("DESTEKLENMEZ", agent.SYSTEM_PROMPT)


class Evaluator(unittest.TestCase):
    def run_all(self, script):
        client = ScriptedClient(script)
        return [evaluate.score(q, agent.run_question(client, q["question"]).tool_calls) for q in QUESTIONS]

    def test_question_set_shape(self):
        self.assertEqual(len(QUESTIONS), 10)
        self.assertEqual(len({q["id"] for q in QUESTIONS}), 10)
        supported = [q for q in QUESTIONS if q["expected_tool"]]
        self.assertGreaterEqual(len(supported), 5)
        for q in supported:   # beklenen parametreler aracın zorunlu alanlarıyla birebir
            self.assertEqual(set(q["expected_params"]), set(tools.TOOLS[q["expected_tool"]]["input_schema"]["required"]), q["id"])
        # kâhin alanları uydurulmamış: yalnızca kaynağı belgelenmiş değer dolu (q02 = kılavuz Örnek 10.3)
        filled = [q["id"] for q in QUESTIONS if q["expected_n_total"] is not None]
        self.assertEqual(filled, ["q02"])
        self.assertEqual(QUESTIONS[1]["expected_n_total"], 390)
        self.assertIn("manual", QUESTIONS[1]["oracle_source"])
        self.assertTrue(all(q["expected_power"] is None for q in QUESTIONS))

    def test_perfect_agent_scores_full(self):
        s = evaluate.summarize(self.run_all(perfect_script()))
        self.assertEqual(s["arac_secimi"]["oran"], 1.0)
        self.assertEqual(s["parametreler"]["oran"], 1.0)
        self.assertEqual(s["N_tam_eslesme"]["olculen"], 1)  # yalnızca kaynaklı q02 ölçülür; diğerleri "ölçülmedi", 0 değil
        self.assertEqual(s["N_tam_eslesme"]["oran"], 1.0)

    def test_wrong_group_count_is_caught(self):
        script = perfect_script()
        q5 = QUESTIONS[4]   # 3 tedavi + 1 kontrol = 4 grup; ajan 3 sayarsa yakalanmalı
        script[q5["question"]] = ("tool", q5["expected_tool"], {**q5["expected_params"], "groups": 3})
        scores = self.run_all(script)
        self.assertTrue(scores[4]["tool_ok"])
        self.assertFalse(scores[4]["params_ok"])

    def test_calling_a_tool_on_unsupported_question_is_caught(self):
        script = perfect_script()
        q7 = QUESTIONS[6]
        script[q7["question"]] = ("tool", "anova_oneway_a_priori", {"f": 0.25, "alpha": 0.05, "power": 0.95, "groups": 2})
        self.assertFalse(self.run_all(script)[6]["tool_ok"])

    def test_percent_not_converted_is_caught(self):
        script = perfect_script()
        q1 = QUESTIONS[0]
        script[q1["question"]] = ("tool", q1["expected_tool"], {**q1["expected_params"], "power": 80})
        self.assertFalse(self.run_all(script)[0]["params_ok"])

    def test_n_metric_activates_only_when_oracle_filled(self):
        q = dict(QUESTIONS[0])
        calls = [{"name": q["expected_tool"], "arguments": q["expected_params"],
                  "result": tools.call(q["expected_tool"], q["expected_params"])}]
        self.assertIsNone(evaluate.score(q, calls)["n_ok"])
        q["expected_n_total"] = calls[0]["result"]["n_total"]
        self.assertTrue(evaluate.score(q, calls)["n_ok"])
        q["expected_n_total"] += 1
        self.assertFalse(evaluate.score(q, calls)["n_ok"])


if __name__ == "__main__":
    unittest.main()
