from domain.cliente_entity import Cliente
from repositories.cliente_repository import ClienteRepository

class ClienteService:
    @staticmethod
    def obtener_todos():
        return ClienteRepository.listar()

    @staticmethod
    def crear(nombre, telefono, email, direccion):
        cliente = Cliente(None, nombre, telefono, email, direccion)
        ClienteRepository.agregar(cliente)
