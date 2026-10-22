"""Araç tanımları: MCP ve ajan katmanlarının ORTAK kaynağı.

Hesap yok. Her araç `engine.compute` çağrısına eşlenir; sonuç CLI ile aynı sözlüktür
(hata: {"error": "..."}). Böylece CLI = MCP = ajan aracı eşitliği yapısal olarak garanti
edilir ve testlerle ölçülür (tests/test_mcp.py).
"""

from __future__ import annotations

from . import engine

# Araç adı -> (test ailesi, mod, açıklama, JSON şeması)
_NUM = {"type": "number"}
TOOLS = {
    "anova_oneway_a_priori": {
        "test": "anova-oneway",
        "mode": "a-priori",
        "description": (
            "Tek yönlü ANOVA (F testi, 2+ bağımsız grup ortalaması) için gerekli toplam örneklem "
            "büyüklüğünü (N) hesaplar. Etki büyüklüğü f (Cohen), anlamlılık düzeyi alpha, "
            "hedef güç ve grup sayısı verilir. Sayıyı motor üretir; çağıran taraf hesap yapmaz."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "f": {**_NUM, "description": "Cohen etki büyüklüğü f (>0). Küçük 0.10, orta 0.25, büyük 0.40."},
                "alpha": {**_NUM, "description": "Birinci tip hata düzeyi, (0,1). Örn. 0.05."},
                "power": {**_NUM, "description": "Hedef güç, (0,1). Örn. 0.80."},
                "groups": {"type": "integer", "description": "Grup (tedavi kolu) sayısı, en az 2."},
            },
            "required": ["f", "alpha", "power", "groups"],
            "additionalProperties": False,
        },
    },
    "anova_oneway_post_hoc": {
        "test": "anova-oneway",
        "mode": "post-hoc",
        "description": (
            "Tek yönlü ANOVA (F testi) için verilen toplam örneklemle elde edilen gücü hesaplar. "
            "Etki büyüklüğü f, alpha, grup sayısı ve toplam N verilir."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "f": {**_NUM, "description": "Cohen etki büyüklüğü f (>0)."},
                "alpha": {**_NUM, "description": "Birinci tip hata düzeyi, (0,1)."},
                "groups": {"type": "integer", "description": "Grup sayısı, en az 2."},
                "n_total": {"type": "integer", "description": "Toplam örneklem büyüklüğü (gruplar toplamı)."},
            },
            "required": ["f", "alpha", "groups", "n_total"],
            "additionalProperties": False,
        },
    },
}


def call(name: str, arguments: dict) -> dict:
    """Aracı çalıştırır. Başarı: sözleşme sözlüğü; hata: {"error": "..."} (özel durum fırlatmaz)."""
    spec = TOOLS.get(name)
    if spec is None:
        return {"error": f"bilinmeyen araç: {name}"}
    try:
        return engine.compute(spec["test"], spec["mode"], dict(arguments or {}))
    except engine.InputError as e:
        return {"error": str(e)}
