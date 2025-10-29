import customtkinter as ctk
from PIL import Image
from ui.views.cliente_view import ClienteView
from ui.views.dashboard import DashboardView
from ui.views.reparacion_view import ReparacionView
from ui.views.inventario_view import InventarioView
from ui.views.ventas_compras import VentasComprasView


class TallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Taller Mecánico")
        self.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.icon_logo = ctk.CTkImage(
            Image.open("ui/assets/icons/carB.png"),  # ruta a tu ícono
            size=(30, 30)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="Taller Mecánico",
            image=self.icon_logo,
            compound="left",   # muestra imagen a la izquierda del texto
            font=("Roboto", 18, "bold"),
            padx=10
        ).pack(pady=20)

        # === Íconos normales y de hover ===
        self.icons = {
            "dashboard": {
                "normal": ctk.CTkImage(Image.open("ui/assets/icons/dashboardB.png"), size=(20, 20)),
                "hover": ctk.CTkImage(Image.open("ui/assets/icons/dashboard.png"), size=(20, 20)),
            },
            "ordenes": {
                "normal": ctk.CTkImage(Image.open("ui/assets/icons/assignmentB.png"), size=(20, 20)),
                "hover": ctk.CTkImage(Image.open("ui/assets/icons/assignment.png"), size=(20, 20)),
            },
            "clientes": {
                "normal": ctk.CTkImage(Image.open("ui/assets/icons/groupB.png"), size=(20, 20)),
                "hover": ctk.CTkImage(Image.open("ui/assets/icons/group.png"), size=(20, 20)),
            },

            "inventario": {
                "normal": ctk.CTkImage(Image.open("ui/assets/icons/inventoryB.png"), size=(20, 20)),
                "hover": ctk.CTkImage(Image.open("ui/assets/icons/inventory.png"), size=(20, 20)),
            },
            "ventas_compras": {
                "normal": ctk.CTkImage(Image.open("ui/assets/icons/shoppingB.png"), size=(20, 20)),
                "hover": ctk.CTkImage(Image.open("ui/assets/icons/shopping.png"), size=(20, 20)),
            },
            "salir": {
                "normal": ctk.CTkImage(Image.open("ui/assets/icons/salirB.png"), size=(20, 20))
            }
        }

        # Botones laterales
        self.buttons = {}

        self.add_sidebar_button("Dashboard", self.mostrar_dashboard, "dashboard")
        self.add_sidebar_button("Órdenes de Reparación", self.mostrar_reparaciones, "ordenes")
        self.add_sidebar_button("Gestión de Clientes", self.mostrar_clientes, "clientes")
        self.add_sidebar_button("Inventario de Partes", self.mostrar_inventario, "inventario")
        self.add_sidebar_button("Ventas y Compras", self.mostrar_ventas_compras, "ventas_compras")

        # Separador
        ctk.CTkLabel(self.sidebar, text="").pack(pady=10)

        # Botón salir
        ctk.CTkButton(
            self.sidebar,
            text="Salir",
            image=self.icons["salir"]["normal"],
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=self.destroy
        ).pack(side="bottom", pady=20, padx=20, fill="x")

        # Contenedor principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Estado
        self.current_view = None
        self.active_button = None

        self.mostrar_dashboard()

    # ===============================
    #  Crear botón lateral con hover
    # ===============================
    def add_sidebar_button(self, text, command, icon_key):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            image=self.icons[icon_key]["normal"],
            anchor="w",
            fg_color="transparent",
            hover_color="#1f538d",
            command=lambda: self.set_active_button(icon_key, command),
        )
        btn.pack(fill="x", pady=2, padx=10)

        # Guardamos referencia
        self.buttons[icon_key] = btn

        # Eventos de hover (cambio de ícono)
        btn.bind("<Enter>", lambda e, k=icon_key: self.on_hover(k, True))
        btn.bind("<Leave>", lambda e, k=icon_key: self.on_hover(k, False))

    # ===============================
    #   Hover y click
    # ===============================
    def on_hover(self, key, is_hovering):
        if key != self.active_button:
            icon = self.icons[key]["hover" if is_hovering else "normal"]
            self.buttons[key].configure(image=icon)

    def set_active_button(self, key, command):
        # Reset iconos
        if self.active_button and self.active_button in self.icons:
            self.buttons[self.active_button].configure(
                fg_color="transparent",
                image=self.icons[self.active_button]["normal"]
            )

        # Activar el nuevo botón
        self.active_button = key
        self.buttons[key].configure(
            fg_color="#1f538d",
            image=self.icons[key]["hover"]
        )

        # Ejecutar acción
        command()

    # ===============================
    #   Cambio de vistas
    # ===============================
    def mostrar_vista(self, vista):
        # Si hay una vista actual, la ocultamos
        if self.current_view:
            self.current_view.pack_forget()
            self.current_view.destroy()  # destruir la vista anterior

        # Crear la nueva vista
        self.current_view = vista(self.main_frame, self)
        self.current_view.pack(fill="both", expand=True)


    def mostrar_dashboard(self):
        self.mostrar_vista(DashboardView)
    def mostrar_reparaciones(self):
        self.mostrar_vista(ReparacionView)
    def mostrar_clientes(self):
        self.mostrar_vista(ClienteView)
    def mostrar_inventario(self):
        self.mostrar_vista(InventarioView)  
    def mostrar_ventas_compras(self):
        self.mostrar_vista(VentasComprasView)

if __name__ == "__main__":
    app = TallerApp()
    app.mainloop()
