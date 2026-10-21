"""Tek giriş noktası. CLI, REST ve MCP adaptörleri YALNIZCA compute() çağırır.

Hesap mantığı families/ altında yaşar; adaptör katmanında sayı üretilmez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .errors import InputError, UnsupportedFamily
from .families import anova_oneway, t2_indep

__all__ = ["compute", "FAMILIES", "InputError", "UnsupportedFamily"]


@dataclass(frozen=True)
class ModeSpec:
    func: Callable
    required: tuple
    defaults: dict = field(default_factory=dict)

    @property
    def allowed(self) -> set:
        return set(self.required) | set(self.defaults)


FAMILIES = {
    # TAKIM AİLESİ (F testi, tek yönlü ANOVA)
    "anova-oneway": {
        "a-priori": ModeSpec(anova_oneway.a_priori, ("f", "alpha", "power", "groups")),
        "post-hoc": ModeSpec(anova_oneway.post_hoc, ("f", "alpha", "groups", "n_total")),
    },
    # REFERANS (ödev sözleşmesi örneği); teslimden önce silinebilir
    "t2-indep": {
        "a-priori": ModeSpec(t2_indep.a_priori, ("d", "alpha", "power"), {"tails": 2, "ratio": 1.0}),
        "post-hoc": ModeSpec(t2_indep.post_hoc, ("d", "alpha", "n1", "n2"), {"tails": 2}),
    },
}


def compute(test: str, mode: str, params: dict) -> dict:
    """Doğrular, dağıtır, sözleşme sözlüğü döndürür. Hata: InputError / UnsupportedFamily."""
    fam = FAMILIES.get(test)
    if fam is None:
        raise UnsupportedFamily(f"desteklenmeyen test ailesi: {test}")
    spec = fam.get(mode)
    if spec is None:
        raise InputError(f"{test} için {mode} modu yok")
    extra = sorted(set(params) - spec.allowed)
    if extra:
        raise InputError(f"{test} / {mode} için kullanılmayan parametre: " + ", ".join("--" + e.replace("_", "-") for e in extra))
    merged = {**spec.defaults, **params}
    missing = [r for r in spec.required if r not in merged]
    if missing:
        raise InputError("zorunlu parametre eksik: " + ", ".join("--" + m.replace("_", "-") for m in missing))
    return spec.func(**merged).as_contract_dict()
