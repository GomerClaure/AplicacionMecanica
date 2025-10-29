import customtkinter as ctk

class ReparacionView(ctk.CTkFrame):
    """Vista simple para registro de reparaciones (sólo título)."""
    def __init__(self, master, app=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app = app

        title = ctk.CTkLabel(self, text="Registro de Reparaciones", font=("Roboto", 20, "bold"))
        title.pack(pady=20)
