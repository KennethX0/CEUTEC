import os
import mysql.connector


class ConexionDB:
    def __init__(self, host=None, user=None, password=None, database=None, port=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conexion = None

    def crear_conexion(self):
        try:
            self.conexion = mysql.connector.connect(
                host=self.host or os.getenv("MYSQL_HOST"),
                user=self.user or os.getenv("MYSQL_USER"),
                password=self.password or os.getenv("MYSQL_PASSWORD"),
                database=self.database or os.getenv("MYSQL_DATABASE"),
                port=int(self.port or os.getenv("MYSQL_PORT", 3306)),
            )
            return self.conexion
        except Exception as error:
            print(f"Error al conectar a MySQL: {error}")
            self.conexion = None
            return None

    def asegurar_conexion(self):
        try:
            if self.conexion is None or not self.conexion.is_connected():
                self.crear_conexion()
        except Exception:
            self.crear_conexion()

        return self.conexion is not None and self.conexion.is_connected()

    def obtener_cursor(self):
        if not self.asegurar_conexion():
            raise RuntimeError('No hay conexion activa a MySQL.')
        # Buffered evita "Commands out of sync" cuando hay resultados pendientes.
        return self.conexion.cursor(buffered=True)

    def cerrar(self):
        if self.conexion is not None:
            try:
                self.conexion.close()
            except Exception:
                pass