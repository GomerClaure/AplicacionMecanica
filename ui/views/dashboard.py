import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    """Vista simple para dashboard (sólo título)."""
    def __init__(self, master, app=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app = app

        title = ctk.CTkLabel(self, text="Dashboard", font=("Roboto", 20, "bold"))
        title.pack(pady=20)
