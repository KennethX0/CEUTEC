import mysql.connector


class ConexionDB:
    def __init__(self, host, user, password, database):
        self.conexion = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )

    def obtener_cursor(self):
        return self.conexion.cursor()