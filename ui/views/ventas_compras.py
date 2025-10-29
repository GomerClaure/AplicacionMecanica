import customtkinter as ctk

class VentasComprasView(ctk.CTkFrame):
    """Vista simple para ventas y compras (sólo título)."""
    def __init__(self, master, app=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app = app

        title = ctk.CTkLabel(self, text="Ventas y Compras", font=("Roboto", 20, "bold"))
        title.pack(pady=20)
