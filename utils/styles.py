"""Configuración de estilos y colores para la UI.
Define colores y temas reutilizables.
"""
APP_COLORS = {
    "primary": "#1f6feb",
    "secondary": "#2b2b2b",
    "success": "#28a745",
    "danger": "#dc3545",
}

DEFAULT_FONT = ("Roboto", 10)


def get_color(name: str, default: str = "#000000") -> str:
    return APP_COLORS.get(name, default)
