import customtkinter as ctk
from config import colors
from PIL import Image
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class TallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Talleric - Sistema de Gestión")
        self.geometry("1100x650")
        self.minsize(1000, 600)

        # === Rutas ===
        self.icon_path = "icons"
        os.makedirs(self.icon_path, exist_ok=True)

        # === Estado de selección ===
        self.active_button = None
        self.buttons = {}  # {button_widget: (icon_normal, icon_hover)}

        # === Layout ===
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#F8F9FC")
        self.sidebar.pack(side="left", fill="y")

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#FFFFFF")
        self.main_frame.pack(side="right", expand=True, fill="both")

        # === Encabezado ===
        ctk.CTkLabel(
    self.sidebar,
    text="Talleric",
    font=("Roboto", 16, "bold"),
    anchor="w",
    justify="left",
    text_color=colors.HEADER_ICON,
    image=self.load_icon("car.png", size=(30, 30)),
    compound="left"  # Muestra el ícono a la izquierda del texto
).pack(padx=20, pady=(30, 10), anchor="w")

        # === Botones ===
        self.create_nav_button("Dashboard", "dashboard.png", "dashboardB.png", self.show_dashboard)
        self.create_nav_button("Órdenes de Reparación", "assignment.png", "assignmentB.png", self.show_ordenes)
        self.create_nav_button("Gestión de Clientes", "group.png", "groupB.png", self.show_clientes)
        self.create_nav_button("Inventario", "inventory.png", "inventoryB.png", self.show_inventario)

        ctk.CTkLabel(self.sidebar, text="").pack(pady=(20, 0))

        # === Vista inicial ===
        self.show_dashboard()
        self.set_active(self.buttons_list[0])  # Marca el primero como activo

    def load_icon(self, filename, size=(20, 20)):
        path = os.path.join(self.icon_path, filename)
        if os.path.exists(path):
            return ctk.CTkImage(Image.open(path), size=size)
        return None

    def create_nav_button(self, text, icon_normal, icon_hover, command):
        icon_n = self.load_icon(icon_normal)
        icon_h = self.load_icon(icon_hover)

        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            image=icon_n,
            anchor="w",
            compound="left",
            fg_color="transparent",
            hover_color=colors.BOTON_NAV_HOVER_BG,
            text_color=colors.BOTON_NAV_INACTIVE,
            font=("Roboto", 14),
            height=40,
            command=lambda b=text, c=command: self.on_nav_click(b, c)
        )
        btn.pack(fill="x", padx=15, pady=2)

        # Eventos de hover
        btn.bind("<Enter>", lambda e, b=btn: self.on_hover(b, True))
        btn.bind("<Leave>", lambda e, b=btn: self.on_hover(b, False))

        # Guardar en lista
        if not hasattr(self, "buttons_list"):
            self.buttons_list = []
        self.buttons_list.append(btn)

        # Guardar íconos
        self.buttons[btn] = (icon_n, icon_h)

    # === Eventos ===
    def on_hover(self, btn, is_hovering):
        if btn == self.active_button:
            return  # no cambiar color si está activo

        icon_n, icon_h = self.buttons[btn]
        btn.configure(
            image=icon_h if is_hovering else icon_n,
            text_color=colors.BOTON_NAV_ACTIVE if is_hovering else colors.BOTON_NAV_INACTIVE
        )

    def on_nav_click(self, name, command):
        for b in self.buttons_list:
            if b.cget("text") == name:
                self.set_active(b)
        command()

    def set_active(self, btn):
        """Activa un botón y desactiva los demás."""
        # Desactivar el anterior
        if self.active_button:
            icon_n, _ = self.buttons[self.active_button]
            self.active_button.configure(
                image=icon_n,
                text_color=colors.BOTON_NAV_INACTIVE,
                fg_color="transparent"
            )

        # Activar el nuevo
        icon_n, icon_h = self.buttons[btn]
        btn.configure(
            image=icon_h,
            text_color=colors.BOTON_NAV_ACTIVE,
            fg_color=colors.BOTON_NAV_HOVER_BG
        )
        self.active_button = btn

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # === Secciones ===
    def show_dashboard(self):
        self.clear_main()
        ctk.CTkLabel(
            self.main_frame, text="📊 Dashboard del Taller",
            font=("Roboto", 24, "bold"), text_color=colors.TEXT_PRIMARY
        ).pack(pady=30)

    def show_ordenes(self):
        self.clear_main()
        ctk.CTkLabel(
            self.main_frame, text="🧾 Órdenes de Reparación",
            font=("Roboto", 24, "bold"), text_color=colors.TEXT_PRIMARY
        ).pack(pady=30)

    def show_clientes(self):
        self.clear_main()
        ctk.CTkLabel(
            self.main_frame, text="👥 Gestión de Clientes",
            font=("Roboto", 24, "bold"), text_color=colors.TEXT_PRIMARY
        ).pack(pady=30)

    def show_inventario(self):
        self.clear_main()
        ctk.CTkLabel(
            self.main_frame, text="📦 Inventario",
            font=("Roboto", 24, "bold"), text_color=colors.TEXT_PRIMARY
        ).pack(pady=30)


if __name__ == "__main__":
    app = TallerApp()
    app.mainloop()
