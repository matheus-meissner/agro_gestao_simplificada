"""
Funções de cálculo (subalgoritmos) relacionadas à perda de colheita.
"""
from typing import Tuple

def calcular_perda_ton(produtividade_t_ha: float, area_ha: float, metodo: str,
                       perda_manual: float = 0.05, perda_mecanica: float = 0.15) -> Tuple[float, float, float]:
    """
    Retorna (perda_pct, perda_ton, total_ton)
    - produtividade_t_ha: toneladas por hectare
    - area_ha: área colhida em hectares
    - metodo: "manual" ou "mecanica"
    - perda_manual / perda_mecanica: frações (0.05 = 5%)
    """
    metodo = metodo.lower()
    if metodo not in ("manual", "mecanica"):
        raise ValueError("método inválido; use 'manual' ou 'mecanica'")

    perda_pct = perda_manual if metodo == "manual" else perda_mecanica
    total_ton = produtividade_t_ha * area_ha
    perda_ton = total_ton * perda_pct
    return (round(perda_pct * 100, 2), round(perda_ton, 2), round(total_ton, 2))
