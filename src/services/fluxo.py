from collections import defaultdict
from typing import List, Dict, Any

def group_by_restaurant(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    resumo = defaultdict(lambda: {"entradas": 0, "saidas": 0})

    for item in items:
        restaurant = item.get("restaurante", "Desconhecido")
        resumo[restaurant]["entradas"] += item.get("totalEntradas", 0)
        resumo[restaurant]["saidas"] += item.get("totalSaidas", 0)

    return dict(resumo)