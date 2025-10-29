import customtkinter as ctk

class InventarioView(ctk.CTkFrame):
    """Vista simple para inventario de partes (sólo título)."""
    def __init__(self, master, app=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app = app

        title = ctk.CTkLabel(self, text="Inventario de Partes", font=("Roboto", 20, "bold"))
        title.pack(pady=20)
