# db_connect.py
import mysql.connector
from mysql.connector import Error

def connect_db():
    """
    Kembalikan objek koneksi MySQL.
    Pastikan MySQL berjalan dan database 'db_hotel' sudah dibuat (atau gunakan setup_database di db.py).
    Sesuaikan host/user/password jika perlu.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",   # isi kalau MySQL pakai password
            database="db_hotel"
        )
        return conn
    except Error as e:
        print("❌ Koneksi gagal:", e)
        return None
