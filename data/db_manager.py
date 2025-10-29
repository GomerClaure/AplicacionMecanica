import sqlite3
import os

DB_PATH = "data/taller.db"

class DBManager:
    @staticmethod
    def connect():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def init_db():
        if not os.path.exists(DB_PATH):
            with open("data/database.sql", "r", encoding="utf-8") as f:
                script = f.read()
            conn = DBManager.connect()
            conn.executescript(script)
            conn.commit()
            conn.close()
