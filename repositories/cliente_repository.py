from data.db_manager import DBManager
from domain.cliente_entity import Cliente

class ClienteRepository:
    @staticmethod
    def listar():
        conn = DBManager.connect()
        rows = conn.execute("SELECT * FROM Clientes").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def agregar(cliente: Cliente):
        conn = DBManager.connect()
        conn.execute("""
            INSERT INTO Clientes (nombre, telefono, email, direccion)
            VALUES (?, ?, ?, ?)
        """, (cliente.nombre, cliente.telefono, cliente.email, cliente.direccion))
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar(cliente_id: int):
        conn = DBManager.connect()
        conn.execute("DELETE FROM Clientes WHERE cliente_id = ?", (cliente_id,))
        conn.commit()
        conn.close()
