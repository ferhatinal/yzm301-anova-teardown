"""Ajan katmanı: Türkçe klinik soruyu doğru araca yönlendirir; HESAP YAPMAZ.

Sayılar yalnızca `tools.call` -> `engine.compute` yolundan gelir. Ajan görevi: test ailesini
seçmek, parametreleri soruya göre çıkarmak (yüzde -> oran, "0,25" -> 0.25), belirsiz ya da
desteklenmeyen durumda araştırmacıya sormak.

Canlı çalıştırma için ANTHROPIC_API_KEY gerekir. YALNIZCA kurgusal araştırma senaryoları
gönderin; gerçek hasta verisi asla gönderilmez (ödev etik kural 5).

  python -m powerlab.agent "Üç kolu f=0,25 ... kaç hasta gerekir?"
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field

from . import tools

DEFAULT_MODEL = os.environ.get("POWERLAB_MODEL", "claude-haiku-5-5")
MAX_TURNS = 6

SYSTEM_PROMPT = """Sen bir klinik araştırma yardımcısısın. Araştırmacıların örneklem büyüklüğü ve güç sorularını Türkçe yanıtlarsın.

KESİN KURALLAR:
1. Örneklem büyüklüğü, güç, kritik değer gibi sayıları ASLA kendin hesaplama ve tahmin etme. Yalnızca araçlardan gelen sayıları aktar.
2. Şu an yalnızca tek yönlü ANOVA (F testi, 2 veya daha fazla grup, etki büyüklüğü f) desteklenir. İki grup için t testi, eşleştirilmiş ölçümler, ki-kare ve regresyon DESTEKLENMEZ; böyle bir soruda araç çağırma, bunun desteklenmediğini söyle.
3. Soruda test ailesini ya da gerekli parametreleri (f, alpha, güç veya N, grup sayısı) belirleyemiyorsan araç çağırma; eksik bilgiyi araştırmacıya sor.
4. Yüzdeleri orana çevir (%80 -> 0.80). Ondalık virgülü noktaya çevir (0,25 -> 0.25). Grup sayısını dikkatle say (üç tedavi ve bir kontrol = 4 grup).
5. Araç hata döndürürse hatayı olduğu gibi aktar; sonucu uydurma.
6. Sonuçta hangi aracı hangi parametrelerle çağırdığını bir cümleyle belirt."""


@dataclass
class Result:
    question: str
    answer: str = ""
    tool_calls: list = field(default_factory=list)   # [{"name","arguments","result"}]
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    turns: int = 0


def anthropic_tool_defs() -> list[dict]:
    return [{"name": n, "description": s["description"], "input_schema": s["input_schema"]}
            for n, s in tools.TOOLS.items()]


def run_question(client, question: str, model: str = DEFAULT_MODEL, max_turns: int = MAX_TURNS) -> Result:
    """Araç kullanım döngüsü. `client`, anthropic.Anthropic (ya da testlerdeki sahte istemci) olabilir."""
    res = Result(question=question)
    messages = [{"role": "user", "content": question}]
    t0 = time.perf_counter()
    for _ in range(max_turns):
        resp = client.messages.create(model=model, max_tokens=1024, system=SYSTEM_PROMPT,
                                      tools=anthropic_tool_defs(), messages=messages)
        res.turns += 1
        res.input_tokens += getattr(resp.usage, "input_tokens", 0)
        res.output_tokens += getattr(resp.usage, "output_tokens", 0)
        uses = [b for b in resp.content if getattr(b, "type", "") == "tool_use"]
        texts = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
        if not uses:
            res.answer = "\n".join(texts).strip()
            break
        messages.append({"role": "assistant", "content": resp.content})
        outputs = []
        for u in uses:
            out = tools.call(u.name, dict(u.input))          # hesap burada, motorda
            res.tool_calls.append({"name": u.name, "arguments": dict(u.input), "result": out})
            outputs.append({"type": "tool_result", "tool_use_id": u.id,
                            "content": json.dumps(out, ensure_ascii=False)})
        messages.append({"role": "user", "content": outputs})
    else:
        res.answer = "(tur sınırına ulaşıldı)"
    res.seconds = time.perf_counter() - t0
    return res


def log_result(res: Result, path: str) -> None:
    """Araç çağrı kaydı (JSONL): ödevin istediği log."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "question": res.question,
            "tool_calls": res.tool_calls, "answer": res.answer,
            "input_tokens": res.input_tokens, "output_tokens": res.output_tokens,
            "seconds": round(res.seconds, 3), "turns": res.turns,
        }, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 2
    import anthropic  # geç içe aktarma: testler anthropic paketi olmadan da çalışsın
    res = run_question(anthropic.Anthropic(), " ".join(argv))
    log_result(res, os.path.join("logs", "agent_calls.jsonl"))
    print(res.answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
