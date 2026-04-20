import os
import mysql.connector


def get_connection():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT", 3306))
        )
        return conexion
    except Exception as e:
        print("ERROR CONECTANDO A MYSQL:", e)
        return None