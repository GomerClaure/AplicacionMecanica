import customtkinter as ctk
from services.cliente_service import ClienteService

class ClienteView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app  # guarda referencia al controlador principal

        ctk.CTkLabel(
            self,
            text="👥 Gestión de Clientes",
            font=("Roboto", 24, "bold")
        ).pack(pady=20)
        # Formulario
        self.nombre = ctk.CTkEntry(self, placeholder_text="Nombre")
        self.telefono = ctk.CTkEntry(self, placeholder_text="Teléfono")
        self.email = ctk.CTkEntry(self, placeholder_text="Email")
        self.direccion = ctk.CTkEntry(self, placeholder_text="Dirección")

        for w in [self.nombre, self.telefono, self.email, self.direccion]:
            w.pack(pady=5)

        ctk.CTkButton(self, text="Registrar Cliente", command=self.guardar_cliente).pack(pady=10)
        ctk.CTkButton(self, text="Actualizar Lista", command=self.listar_clientes).pack(pady=5)

        # Tabla de clientes
        self.text_area = ctk.CTkTextbox(self, height=250)
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)

        self.listar_clientes()

    def guardar_cliente(self):
        ClienteService.crear(
            self.nombre.get(),
            self.telefono.get(),
            self.email.get(),
            self.direccion.get(),
        )
        self.listar_clientes()

    def listar_clientes(self):
        clientes = ClienteService.obtener_todos()
        self.text_area.delete("1.0", "end")
        for c in clientes:
            self.text_area.insert("end", f"{c['cliente_id']} - {c['nombre']} - {c['telefono']} - {c['email']}\n")
