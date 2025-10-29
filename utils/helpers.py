"""Funciones auxiliares generales.
Añade aquí utilidades reutilizables (validaciones, formateo de fechas, etc.).
"""
from typing import Any


def safe_get(d: dict, key: str, default: Any = None) -> Any:
    """Obtener valor de diccionario de forma segura."""
    return d.get(key, default)


def format_currency(value: float, symbol: str = "S/") -> str:
    return f"{symbol}{value:,.2f}"
