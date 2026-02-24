import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="(Lsvs1919)",
        database="atm_system"
    )