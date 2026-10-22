"""10 soruluk değerlendirmeyi çalıştırır.

  python eval/run_eval.py --live            # ANTHROPIC_API_KEY gerekir; logs/agent_calls.jsonl'e yazar
  python eval/run_eval.py --replay logs/agent_calls.jsonl   # mevcut log'u yeniden puanla (API yok)

YALNIZCA kurgusal senaryolar gönderilir; gerçek hasta verisi asla.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from powerlab import agent, evaluate  # noqa: E402

QUESTIONS = os.path.join(ROOT, "eval", "questions.jsonl")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--live", action="store_true")
    g.add_argument("--replay")
    ap.add_argument("--log", default=os.path.join(ROOT, "logs", "agent_calls.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "eval", "results.json"))
    args = ap.parse_args()

    questions = evaluate.load_questions(QUESTIONS)
    runs = {}
    if args.live:
        import anthropic
        client = anthropic.Anthropic()
        for q in questions:
            res = agent.run_question(client, q["question"])
            agent.log_result(res, args.log)
            runs[q["question"]] = {"tool_calls": res.tool_calls, "input_tokens": res.input_tokens,
                                   "output_tokens": res.output_tokens, "seconds": res.seconds}
    else:
        with open(args.replay, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                runs[r["question"]] = r   # aynı soru tekrarlanmışsa sonuncusu geçerli

    scores, usage = [], []
    for q in questions:
        r = runs.get(q["question"])
        if r is None:
            print(f"UYARI: {q['id']} için kayıt yok", file=sys.stderr)
            continue
        scores.append(evaluate.score(q, r["tool_calls"]))
        usage.append(r)
    summary = evaluate.summarize(scores, usage)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"ozet": summary, "sorular": scores}, fh, ensure_ascii=False, indent=2)
    for s in scores:
        print(s["id"], "araç:", s["tool_ok"], "parametre:", s["params_ok"], "N:", s["n_ok"], "çağrılan:", s["called"])
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
