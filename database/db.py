# db.py
"""
Database schema & helper functions for HOTEL management.

Jalankan: python db.py
-> akan membuat tabel jika belum ada dan memasukkan data sample untuk 7 jenis kamar + admin default.

Fungsi utama yang tersedia (dipanggil dari GUI):
- setup_database()
- get_all_rooms()
- get_room_by_id(room_id)
- add_room(...)
- update_room(...)
- delete_room(room_id)
- list_users()
- add_user(username, password, role='user')
- authenticate_user(username, password)
- create_booking(user_id, room_id, check_in, check_out, guests)
- get_all_bookings()
- get_bookings_by_status(status)
- update_booking_status(booking_id, status)
- create_payment(booking_id, amount, method, proof_path=None)
- get_all_payments()
- confirm_payment(payment_id)
- etc.
"""

import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime, date

from db_connect import connect_db

# ---------------------------
# Helper: hashing password
# ---------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------
# Setup database and tables
# ---------------------------
def setup_database(seed_rooms=True):
    conn = connect_db()
    if not conn:
        print("❌ Tidak bisa konek ke DB. Pastikan MySQL hidup dan kredensial benar.")
        return

    cur = conn.cursor()
    # users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE,
        password VARCHAR(255),
        role ENUM('admin','user') DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """)

    # rooms (dengan ukuran, tipe, harga tanpa/plus breakfast, stok)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nama VARCHAR(120),
        tipe VARCHAR(80),
        ukuran VARCHAR(40),
        deskripsi TEXT,
        harga_without_breakfast DECIMAL(10,2),
        harga_with_breakfast DECIMAL(10,2),
        stok INT DEFAULT 10,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """)

    # bookings (lebih lengkap)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kode_booking VARCHAR(50) UNIQUE,
        user_id INT,
        room_id INT,
        check_in DATE,
        check_out DATE,
        guests INT DEFAULT 1,
        total DECIMAL(12,2) DEFAULT 0,
        status ENUM('dibooking','dipesan','selesai','dibatalkan') DEFAULT 'dibooked',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL
    ) ENGINE=InnoDB;
    """)

    # payments (bukti file path optional)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        booking_id INT,
        amount DECIMAL(12,2),
        method VARCHAR(80),
        proof_path VARCHAR(255) NULL,
        paid_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status ENUM('pending','confirmed','rejected') DEFAULT 'pending',
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # Create default admin if not exists
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        pwd_hash = hash_password("123")
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s,%s,%s)",
                    ("admin", pwd_hash, "admin"))
        print("🧩 Admin default dibuat: username=admin password=123")

    conn.commit()

    # Seed rooms sample jika diminta dan jika tabel rooms kosong
    if seed_rooms:
        cur.execute("SELECT COUNT(*) FROM rooms")
        count = cur.fetchone()[0]
        if count == 0:
            seed_sample_rooms(cur)
            conn.commit()
            print("📦 Sample 7 kamar telah ditambahkan.")

    cur.close()
    conn.close()
    print("✅ Setup database selesai.")


def seed_sample_rooms(cursor):
    """
    Tambah 7 tipe kamar sample. Harga disimpan dalam satuan (contoh: 350000.00)
    Ukuran ditulis seperti '20 m²'
    """
    rooms = [
        ("Standard Room", "Superior", "18 m²",
         "Kasur Queen. Pilihan tanpa/termasuk sarapan.", 350000.00, 400000.00, 8),
        ("Superior Room", "Superior", "20 m²",
         "Kasur Queen/King. Pilihan tanpa/termasuk sarapan.", 500000.00, 550000.00, 6),
        ("Deluxe Room", "Deluxe", "24 m²",
         "Kasur Queen/King. Ruang lebih luas, cocok kerja.", 700000.00, 780000.00, 5),
        ("Twin Room", "Twin", "24 m²",
         "Dua kasur single. Cocok 2 tamu.", 600000.00, 660000.00, 6),
        ("Family Room", "Family", "35 m²",
         "Kasur King + ekstra tempat tidur. Ruang keluarga.", 900000.00, 990000.00, 3),
        ("Suite Room", "Suite", "45 m²",
         "Suite dengan ruang tamu. Fasilitas premium.", 1500000.00, 1650000.00, 2),
        ("Presidential Room", "Presidential", "80 m²",
         "Unit mewah dengan ruang tamu & dining. Sangat luas.", 3000000.00, 3300000.00, 1),
    ]
    sql = """INSERT INTO rooms
             (nama, tipe, ukuran, deskripsi, harga_without_breakfast, harga_with_breakfast, stok)
             VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    cursor.executemany(sql, rooms)


# ---------------------------
# Room functions
# ---------------------------
def get_all_rooms():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM rooms ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_room_by_id(room_id):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM rooms WHERE id=%s", (room_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def add_room(nama, tipe, ukuran, deskripsi, price_without, price_with, stok=10):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    cur.execute("""INSERT INTO rooms
                   (nama, tipe, ukuran, deskripsi, harga_without_breakfast, harga_with_breakfast, stok)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (nama, tipe, ukuran, deskripsi, price_without, price_with, stok))
    conn.commit()
    cur.close()
    conn.close()
    return True


def update_room(room_id, **kwargs):
    # kwargs: nama, tipe, ukuran, deskripsi, price_without, price_with, stok
    allowed = {
        "nama": "nama",
        "tipe": "tipe",
        "ukuran": "ukuran",
        "deskripsi": "deskripsi",
        "price_without": "harga_without_breakfast",
        "price_with": "harga_with_breakfast",
        "stok": "stok"
    }
    parts = []
    vals = []
    for k, v in kwargs.items():
        if k in allowed:
            parts.append(f"{allowed[k]}=%s")
            vals.append(v)
    if not parts:
        return False
    vals.append(room_id)
    sql = f"UPDATE rooms SET {', '.join(parts)} WHERE id=%s"
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    cur.execute(sql, tuple(vals))
    conn.commit()
    cur.close()
    conn.close()
    return True


def delete_room(room_id):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    cur.execute("DELETE FROM rooms WHERE id=%s", (room_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True


# ---------------------------
# User functions
# ---------------------------
def list_users():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_user(username, password, role="user"):
    conn = connect_db()
    if not conn:
        return False, "DB connection failed"
    cur = conn.cursor()
    hashed = hash_password(password)
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s,%s,%s)",
                    (username, hashed, role))
        conn.commit()
        return True, None
    except mysql.connector.IntegrityError as e:
        return False, "username already exists"
    finally:
        cur.close()
        conn.close()


def authenticate_user(username, password):
    conn = connect_db()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    if row["password"] == hash_password(password):
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None


# ---------------------------
# Booking & Payment functions
# ---------------------------
def generate_booking_code():
    # simple code: BK-YYYYMMDD-HHMMSS-rand
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"BK-{now}"


def create_booking(user_id, room_id, check_in: date, check_out: date, guests=1, include_breakfast=False):
    """
    Buat booking dan kembalikan id booking.
    Perhitungan total: harga * nights. Pilih price_with_breakfast jika include_breakfast = True.
    """
    conn = connect_db()
    if not conn:
        return None, "DB connection failed"
    cur = conn.cursor()
    # ambil harga
    cur.execute("SELECT harga_with_breakfast, harga_without_breakfast, stok FROM rooms WHERE id=%s", (room_id,))
    r = cur.fetchone()
    if not r:
        cur.close()
        conn.close()
        return None, "Room not found"
    # r is tuple
    price_with, price_without, stok = r[0], r[1], r[2]
    nights = (check_out - check_in).days
    if nights <= 0:
        nights = 1
    price_per_night = price_with if include_breakfast else price_without
    total = float(price_per_night) * nights
    kode = generate_booking_code()
    cur.execute("""INSERT INTO bookings
                   (kode_booking, user_id, room_id, check_in, check_out, guests, total, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (kode, user_id, room_id, check_in, check_out, guests, total, 'dipesan'))
    booking_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return booking_id, None


def get_all_bookings():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, u.username AS user_name, r.nama AS room_name
        FROM bookings b
        LEFT JOIN users u ON b.user_id = u.id
        LEFT JOIN rooms r ON b.room_id = r.id
        ORDER BY b.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_bookings_by_status(status):
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT b.*, u.username AS user_name, r.nama AS room_name
        FROM bookings b
        LEFT JOIN users u ON b.user_id = u.id
        LEFT JOIN rooms r ON b.room_id = r.id
        WHERE b.status=%s
        ORDER BY b.created_at DESC
    """, (status,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_booking_status(booking_id, status):
    conn = connect_db()
    if not conn:
        return False
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status=%s WHERE id=%s", (status, booking_id))
    conn.commit()
    cur.close()
    conn.close()
    return True


# Payments
def create_payment(booking_id, amount, method, proof_path=None):
    conn = connect_db()
    if not conn:
        return None, "DB connection failed"
    cur = conn.cursor()
    cur.execute("INSERT INTO payments (booking_id, amount, method, proof_path, status) VALUES (%s,%s,%s,%s,%s)",
                (booking_id, amount, method, proof_path, 'pending'))
    pid = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return pid, None


def get_all_payments():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, b.kode_booking, u.username AS user_name
        FROM payments p
        LEFT JOIN bookings b ON p.booking_id = b.id
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY p.paid_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def confirm_payment(payment_id):
    conn = connect_db()
    if not conn:
        return False, "DB connection failed"
    cur = conn.cursor()
    # set payment confirmed
    cur.execute("UPDATE payments SET status='confirmed' WHERE id=%s", (payment_id,))
    # optionally set booking status to 'dipesan' -> 'dipesan' already used: we'll set to 'dipesan' or 'selesai' depending logic
    # Get booking_id
    cur.execute("SELECT booking_id FROM payments WHERE id=%s", (payment_id,))
    r = cur.fetchone()
    if r:
        booking_id = r[0]
        cur.execute("UPDATE bookings SET status='dipesan' WHERE id=%s", (booking_id,))
    conn.commit()
    cur.close()
    conn.close()
    return True, None


# ---------------------------
# If run as script: setup
# ---------------------------
if __name__ == "__main__":
    setup_database(seed_rooms=True)
