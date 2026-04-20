import mysql.connector


class ConexionDB:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conexion = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def asegurar_conexion(self):
        try:
            if self.conexion is None or not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )
        except Exception:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )

    def obtener_cursor(self):
        self.asegurar_conexion()
        # Buffered evita "Commands out of sync" cuando hay resultados pendientes.
        return self.conexion.cursor(buffered=True)