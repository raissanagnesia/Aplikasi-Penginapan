# -*- coding: utf-8 -*-
import sys
import os
import hashlib
import csv
from datetime import datetime

# Add parent directory to sys.path so 'database' module can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QApplication, QMessageBox, QFileDialog
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument

# Import database connection
from database.db_connect import connect_db

# Import UI modules
from tampilan_awal import Ui_WelcomeForm
from login import Ui_LoginForm
from register import Ui_RegisterForm
from dashboard_admin import Ui_DashboardAdmin as Ui_DashboardAdminUI

# Dashboard user may not exist
try:
    from dashboard_user import Ui_DashboardAdmin as Ui_DashboardUserUI
except Exception:
    Ui_DashboardUserUI = Ui_DashboardAdminUI

# Supporting UI modules
from tambah import Ui_TambahKamar as Ui_TambahKamarForm
from edit import Ui_TambahKamar as Ui_EditKamarForm
from hapus_kamar import Ui_TambahKamar as Ui_HapusKamarForm
from lihat_bukti_tf import Ui_WidgetDataTransfer as Ui_LihatBuktiTransfer
from konfirmasi_pembayaran import Ui_WidgetDataTransfer as Ui_KonfirmasiPembayaran
from lihat_rating import Ui_DialogDetailUlasan
from hapus_rating import Ui_WidgetHapusRating
from hapus_kritik import Ui_WidgetKritikSaran


# ========== Database Functions ==========

def check_credentials(username: str, password: str):
    """Check username/password against users table. Returns user dict or None."""
    try:
        conn = connect_db()
        if conn is None:
            print("ERROR: DB connection returned None")
            return None
        
        cursor = conn.cursor(dictionary=True)
        hashed = hashlib.sha256(password.encode()).hexdigest()
        print(f"DEBUG: Querying user '{username}' with hash starting {hashed[:8]}...")
        cursor.execute("SELECT id, username, role FROM users WHERE username=%s AND password=%s", 
                      (username, hashed))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            print(f"DEBUG: User found - {row}")
        else:
            print(f"DEBUG: No user found")
        return row
    except Exception as e:
        print(f"ERROR in check_credentials: {e}")
        import traceback
        traceback.print_exc()
        return None


# ========== Screen Classes ==========

class WelcomeScreen(QtWidgets.QWidget):
    switch_to_login = QtCore.pyqtSignal()
    switch_to_register = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WelcomeForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btnLogin"):
            self.ui.btnLogin.clicked.connect(self.switch_to_login.emit)
        if hasattr(self.ui, "btnRegister"):
            self.ui.btnRegister.clicked.connect(self.switch_to_register.emit)


class LoginScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()
    switch_to_dashboard = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btnLogin"):
            self.ui.btnLogin.clicked.connect(self.handle_login)

    def handle_login(self):
        uname = getattr(self.ui, "txtUsername", None)
        pwd = getattr(self.ui, "txtPassword", None)
        username = uname.text().strip() if uname is not None else ""
        password = pwd.text().strip() if pwd is not None else ""
        
        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan Password harus diisi!")
            return
        
        print(f"DEBUG: Attempting login for user '{username}'")
        user = check_credentials(username, password)
        
        if user:
            role = user.get('role', 'user')
            QMessageBox.information(self, "Login Berhasil", 
                                   f"Selamat datang {user.get('username')} ({role})")
            if uname is not None: 
                uname.clear()
            if pwd is not None: 
                pwd.clear()
            self.switch_to_dashboard.emit((user.get('username'), role))
        else:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah!")


class RegisterScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btnRegister"):
            self.ui.btnRegister.clicked.connect(self.handle_register)

    def handle_register(self):
        get = lambda n: getattr(self.ui, n, None)
        vals = {}
        for name in ("txtUsername", "txtPassword", "txtNama", "txtEmail", "txtWA"):
            w = get(name)
            vals[name] = w.text().strip() if w is not None else ""
        
        if not all(vals.values()):
            QMessageBox.warning(self, "Registrasi Gagal", "Semua field harus diisi!")
            return
        
        hashed = hashlib.sha256(vals['txtPassword'].encode()).hexdigest()
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (vals['txtUsername'], hashed, 'user')
            )
            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Registrasi Berhasil", 
                                   f"Akun berhasil dibuat! Silakan login.")
            self.reset_form()
            self.switch_to_welcome.emit()
        except Exception as e:
            QMessageBox.critical(self, "Registrasi Gagal", f"Error: {str(e)}")

    def reset_form(self):
        for name in ("txtUsername", "txtPassword", "txtNama", "txtEmail", "txtWA"):
            w = getattr(self.ui, name, None)
            if w is not None:
                w.clear()


class AdminDashboardScreen(QtWidgets.QWidget):
    show_tambah_kamar = QtCore.pyqtSignal()
    show_edit_kamar = QtCore.pyqtSignal()
    show_hapus_kamar = QtCore.pyqtSignal()
    show_lihat_bukti = QtCore.pyqtSignal()
    show_konfirmasi_pembayaran = QtCore.pyqtSignal()
    show_lihat_rating = QtCore.pyqtSignal()
    show_hapus_rating = QtCore.pyqtSignal()
    show_hapus_kritik = QtCore.pyqtSignal()
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self, username="admin"):
        super().__init__()
        self.username = username
        self.ui = Ui_DashboardAdminUI()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Admin Dashboard - {username}")
        self._connect_buttons()

    def _connect_buttons(self):
        mapping = {
            "btnAddRoom": self.show_tambah_kamar,
            "btnEditRoom": self.show_edit_kamar,
            "btnDeleteRoom": self.show_hapus_kamar,
            "btnViewPaymentProof": self.show_lihat_bukti,
            "btnValidatePayment": self.show_konfirmasi_pembayaran,
            "btnViewRoomRatings": self.show_lihat_rating,
            "btnDeleteRating": self.show_hapus_rating,
            "btnDeleteFeedback": self.show_hapus_kritik,
            "btnLogout": self.switch_to_welcome,
        }
        
        for btn_name, signal in mapping.items():
            btn = getattr(self.ui, btn_name, None)
            if btn is not None:
                btn.clicked.connect(signal.emit)


class UserDashboardScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self, username="User"):
        super().__init__()
        self.username = username
        self.ui = Ui_DashboardUserUI()
        self.ui.setupUi(self)
        self.setWindowTitle(f"User Dashboard - {username}")
        
        if hasattr(self.ui, "btnLogout"):
            self.ui.btnLogout.clicked.connect(self.switch_to_welcome.emit)


class TambahKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_TambahKamarForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self._handle_tambah)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self._pilih_gambar)
        if hasattr(self.ui, "pushButton_2"):
            self.ui.pushButton_2.clicked.connect(self.back_to_dashboard.emit)

    def _handle_tambah(self):
        nama = getattr(self.ui, "input_nama", None)
        if nama is not None and nama.text().strip():
            QMessageBox.information(self, "Berhasil", 
                                   f"Kamar '{nama.text().strip()}' berhasil ditambahkan.")
            self.back_to_dashboard.emit()
        else:
            QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")

    def _pilih_gambar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", 
                                              "Images (*.png *.jpg *.jpeg *.bmp)")
        if path and hasattr(self.ui, "lineEdit"):
            self.ui.lineEdit.setText(path)


class EditKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_EditKamarForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self._handle_edit)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self._pilih_gambar)
        if hasattr(self.ui, "pushButton_2"):
            self.ui.pushButton_2.clicked.connect(self.back_to_dashboard.emit)

    def _handle_edit(self):
        nama = getattr(self.ui, "input_nama", None)
        if nama is not None and nama.text().strip():
            QMessageBox.information(self, "Berhasil", 
                                   f"Kamar '{nama.text().strip()}' berhasil diupdate.")
            self.back_to_dashboard.emit()
        else:
            QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")

    def _pilih_gambar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", 
                                              "Images (*.png *.jpg *.jpeg *.bmp)")
        if path and hasattr(self.ui, "lineEdit"):
            self.ui.lineEdit.setText(path)


class HapusKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_HapusKamarForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self._handle_hapus)
        if hasattr(self.ui, "pushButton_2"):
            self.ui.pushButton_2.clicked.connect(self.back_to_dashboard.emit)

    def _handle_hapus(self):
        nama = getattr(self.ui, "input_nama", None)
        if nama is not None and nama.text().strip():
            reply = QMessageBox.question(self, "Konfirmasi", 
                                        f"Hapus kamar '{nama.text().strip()}'?", 
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "Berhasil", "Kamar berhasil dihapus.")
                self.back_to_dashboard.emit()
        else:
            QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")


class LihatBuktiScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_LihatBuktiTransfer()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


class KonfirmasiPembayaranScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_KonfirmasiPembayaran()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


class LihatRatingScreen(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DialogDetailUlasan()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.close)


class HapusRatingScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetHapusRating()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


class HapusKritikScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetKritikSaran()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


# ========== MainWindow ==========

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏨 Aplikasi Penginapan 🏨")
        self.setGeometry(100, 100, 1000, 700)

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.current_username = None
        self.current_role = None

        self.welcome = WelcomeScreen()
        self.login = LoginScreen()
        self.register = RegisterScreen()
        self.admin_dash = None
        self.user_dash = None

        self.tambah = TambahKamarScreen()
        self.edit = EditKamarScreen()
        self.hapus_kamar = HapusKamarScreen()
        self.lihat_bukti = LihatBuktiScreen()
        self.konfirmasi = KonfirmasiPembayaranScreen()
        self.lihat_rating = LihatRatingScreen()
        self.hapus_rating = HapusRatingScreen()
        self.hapus_kritik = HapusKritikScreen()

        for w in (self.welcome, self.login, self.register,
                  self.tambah, self.edit, self.hapus_kamar,
                  self.lihat_bukti, self.konfirmasi, self.hapus_rating,
                  self.hapus_kritik):
            self.stacked.addWidget(w)

        self._connect_signals()
        self.stacked.setCurrentWidget(self.welcome)

    def _connect_signals(self):
        self.welcome.switch_to_login.connect(lambda: self.stacked.setCurrentWidget(self.login))
        self.welcome.switch_to_register.connect(lambda: self.stacked.setCurrentWidget(self.register))

        self.login.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))
        self.login.switch_to_dashboard.connect(self.show_dashboard_from_payload)
        self.register.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))

        for w in (self.tambah, self.edit, self.hapus_kamar,
                  self.lihat_bukti, self.konfirmasi, self.hapus_rating,
                  self.hapus_kritik):
            if hasattr(w, "back_to_dashboard"):
                w.back_to_dashboard.connect(self._show_dashboard_current)

    def show_dashboard_from_payload(self, payload):
        username, role = ("", "user")
        if isinstance(payload, tuple) and len(payload) == 2:
            username, role = payload
        elif isinstance(payload, str):
            username = payload
        
        self.current_username = username or ""
        self.current_role = role or "user"
        
        if role == "admin":
            if self.admin_dash is None:
                self.admin_dash = AdminDashboardScreen(username=self.current_username)
                self.admin_dash.show_tambah_kamar.connect(
                    lambda: self.stacked.setCurrentWidget(self.tambah))
                self.admin_dash.show_edit_kamar.connect(
                    lambda: self.stacked.setCurrentWidget(self.edit))
                self.admin_dash.show_hapus_kamar.connect(
                    lambda: self.stacked.setCurrentWidget(self.hapus_kamar))
                self.admin_dash.show_lihat_bukti.connect(
                    lambda: self.stacked.setCurrentWidget(self.lihat_bukti))
                self.admin_dash.show_konfirmasi_pembayaran.connect(
                    lambda: self.stacked.setCurrentWidget(self.konfirmasi))
                self.admin_dash.show_lihat_rating.connect(
                    lambda: self.lihat_rating.show())
                self.admin_dash.show_hapus_rating.connect(
                    lambda: self.stacked.setCurrentWidget(self.hapus_rating))
                self.admin_dash.show_hapus_kritik.connect(
                    lambda: self.stacked.setCurrentWidget(self.hapus_kritik))
                self.admin_dash.switch_to_welcome.connect(
                    lambda: self.stacked.setCurrentWidget(self.welcome))
                self.stacked.addWidget(self.admin_dash)
            self.stacked.setCurrentWidget(self.admin_dash)
        else:
            if self.user_dash is None:
                self.user_dash = UserDashboardScreen(username=self.current_username)
                if hasattr(self.user_dash.ui, "btnLogout"):
                    self.user_dash.ui.btnLogout.clicked.connect(
                        lambda: self.stacked.setCurrentWidget(self.welcome))
                self.stacked.addWidget(self.user_dash)
            self.stacked.setCurrentWidget(self.user_dash)

    def _show_dashboard_current(self):
        if self.current_role == "admin":
            if self.admin_dash is not None:
                self.stacked.setCurrentWidget(self.admin_dash)
            else:
                self.stacked.setCurrentWidget(self.welcome)
        else:
            if self.user_dash is not None:
                self.stacked.setCurrentWidget(self.user_dash)
            else:
                self.stacked.setCurrentWidget(self.welcome)


def main():
    """Main application entry point with DB check"""
    print("Starting application...")
    app = QApplication(sys.argv)

    print("Checking database connectivity...")
    
    # Try to connect to DB once with timeout
    try:
        print("Attempting to connect to database...")
        conn = connect_db()
        if conn is not None:
            print("✓ Database connection successful!")
            try:
                conn.close()
            except:
                pass
        else:
            print("✓ Database connection returned None but continuing...")
    except Exception as e:
        print(f"⚠ Database connection warning: {e}")
        print("Continuing with application anyway...")

    print("Launching main window...")
    w = MainWindow()
    w.show()
    print("Application running...")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()



class WelcomeScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()
    switch_to_dashboard = QtCore.pyqtSignal(object)  # emit (username, role)

    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btnLogin"):
            self.ui.btnLogin.clicked.connect(self.handle_login)

    def handle_login(self):
        uname = getattr(self.ui, "txtUsername", None)
        pwd = getattr(self.ui, "txtPassword", None)
        username = uname.text().strip() if uname is not None else ""
        password = pwd.text().strip() if pwd is not None else ""
        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan Password harus diisi!")
            return
        # Check credentials against database
        try:
            user = check_credentials(username, password)
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Gagal akses database: {e}")
            return
        if not user:
            QMessageBox.warning(self, "Login Gagal", "Username atau password salah!")
            return
        role = user.get('role', 'user')
        QMessageBox.information(self, "Login Berhasil", f"Selamat datang {user.get('username')} ({role})")
        # clear fields
        if uname is not None: uname.clear()
        if pwd is not None: pwd.clear()
        # emit username and role as payload
        self.switch_to_dashboard.emit((user.get('username'), role))


class RegisterScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btnRegister"):
            self.ui.btnRegister.clicked.connect(self.handle_register)

    def handle_register(self):
        get = lambda n: getattr(self.ui, n, None)
        vals = []
        for name in ("txtUsername", "txtPassword", "txtNama", "txtEmail", "txtWA"):
            w = get(name)
            vals.append(w.text().strip() if w is not None else "")
        if not all(vals):
            QMessageBox.warning(self, "Registrasi Gagal", "Semua field harus diisi!")
            return
        QMessageBox.information(self, "Registrasi Berhasil", f"Selamat datang {vals[2]}! Silakan login.")
        self.reset_form()
        self.switch_to_welcome.emit()

    def reset_form(self):
        for name in ("txtUsername", "txtPassword", "txtNama", "txtEmail", "txtWA"):
            w = getattr(self.ui, name, None)
            if w is not None:
                w.clear()


class AdminDashboardScreen(QtWidgets.QWidget):
    show_tambah_kamar = QtCore.pyqtSignal()
    show_edit_kamar = QtCore.pyqtSignal()
    show_hapus_kamar = QtCore.pyqtSignal()
    show_lihat_bukti = QtCore.pyqtSignal()
    show_konfirmasi_pembayaran = QtCore.pyqtSignal()
    show_lihat_rating = QtCore.pyqtSignal()
    show_hapus_rating = QtCore.pyqtSignal()
    show_hapus_kritik = QtCore.pyqtSignal()
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self, username="admin"):
        super().__init__()
        self.ui = Ui_DashboardAdminUI()
        self.ui.setupUi(self)
        self.username = username
        self._connect_buttons()

    def _connect_buttons(self):
        # connect known names safely; UI may have different object names
        mapping = {
            "btnAddRoom": self.show_tambah_kamar,
            "btnEditRoom": self.show_edit_kamar,
            "btnDeleteRoom": self.show_hapus_kamar,
            "btnViewPaymentProof": self.show_lihat_bukti,
            "btnValidatePayment": self.show_konfirmasi_pembayaran,
            "btnViewRoomRatings": self.show_lihat_rating,
            "btnDeleteRating": self.show_hapus_rating,
            "btnDeleteFeedback": self.show_hapus_kritik,
            "btnLogout": self.switch_to_welcome,
            # new buttons for functionality
            "btnRefreshData": None,
            "btnExportPdf": None,
            "btnGenerateReport": None
        }
        for name, sig in mapping.items():
            w = getattr(self.ui, name, None)
            if w is not None:
                if name == "btnRefreshData":
                    w.clicked.connect(self.refresh_data)
                elif name == "btnExportPdf":
                    w.clicked.connect(self.export_pdf)
                elif name == "btnGenerateReport":
                    w.clicked.connect(self.generate_laporan)
                else:
                    # existing mapping: sig is a signal object stored above
                    if sig is not None:
                        w.clicked.connect(sig.emit)

    # ---------- Added functions ----------

    def refresh_data(self):
        """
        Placeholder refresh: try to find common tables and reload placeholder data.
        Replace this with actual data reloading from your data source.
        """
        updated = False
        # Try common table names used in UI
        table_names = ["tablePayments", "tableBooking", "tableKritik", "tableRooms"]
        for name in table_names:
            table = getattr(self.ui, name, None)
            if table is not None and isinstance(table, QtWidgets.QTableWidget):
                # clear and add a placeholder row (simulate refresh)
                table.clearContents()
                table.setRowCount(1)
                # fill with placeholder values depending on column count
                cols = table.columnCount() or 1
                for c in range(cols):
                    item = QtWidgets.QTableWidgetItem(f"Refreshed {name} col{c+1}")
                    table.setItem(0, c, item)
                updated = True
        if updated:
            QMessageBox.information(self, "Refresh Data", "Data berhasil direfresh (placeholder).")
        else:
            QMessageBox.information(self, "Refresh Data", "Tidak ada tabel yang dapat direfresh pada UI.")

    def _table_to_html(self, table):
        """Convert QTableWidget to simple HTML table"""
        rows = table.rowCount()
        cols = table.columnCount()
        # header
        headers = []
        for c in range(cols):
            hitem = table.horizontalHeaderItem(c)
            headers.append(hitem.text() if hitem is not None else f"Col{c+1}")
        html = "<table border='1' cellspacing='0' cellpadding='4'>"
        # header row
        html += "<tr>"
        for h in headers:
            html += f"<th>{QtCore.QCoreApplication.translate('', h)}</th>"
        html += "</tr>"
        # data rows
        for r in range(rows):
            html += "<tr>"
            for c in range(cols):
                item = table.item(r, c)
                html += f"<td>{item.text() if item is not None else ''}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    def export_pdf(self):
        """
        Export first available table to PDF using Qt printing (QPrinter).
        """
        # try selection order
        table_candidates = ["tablePayments", "tableBooking", "tableRooms", "tableKritik"]
        table = None
        for name in table_candidates:
            t = getattr(self.ui, name, None)
            if t is not None and isinstance(t, QtWidgets.QTableWidget):
                table = t
                break
        if table is None:
            QMessageBox.warning(self, "Export PDF", "Tidak ditemukan tabel untuk diexport.")
            return

        fname, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", os.path.expanduser("~/report.pdf"), "PDF files (*.pdf)")
        if not fname:
            return

        # build simple HTML document
        html = f"<h2>Laporan - {self.username} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>"
        html += self._table_to_html(table)
        doc = QTextDocument()
        doc.setHtml(html)

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(fname)
        # optional: set page size / margins
        doc.print_(printer)
        QMessageBox.information(self, "Export PDF", f"PDF berhasil disimpan: {fname}")

    def generate_laporan(self):
        """
        Generate CSV report aggregating available tables and save to reports/ with timestamp.
        """
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join("reports", f"laporan_{timestamp}.csv")

        # collect table data
        collected = []
        for name in ("tablePayments", "tableBooking", "tableRooms", "tableKritik"):
            t = getattr(self.ui, name, None)
            if t is None or not isinstance(t, QtWidgets.QTableWidget):
                continue
            # header
            headers = []
            for c in range(t.columnCount()):
                hitem = t.horizontalHeaderItem(c)
                headers.append(hitem.text() if hitem is not None else f"Col{c+1}")
            # rows
            for r in range(t.rowCount()):
                row = []
                for c in range(t.columnCount()):
                    it = t.item(r, c)
                    row.append(it.text() if it is not None else "")
                collected.append((name, headers, row))

        if not collected:
            QMessageBox.information(self, "Generate Laporan", "Tidak ada data tabel untuk dibuat laporan.")
            return

        # write CSV: first columns = source_table, then headers and row values
        with open(csv_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["sumber_tabel", "kolom", "nilai"])
            for source, headers, row in collected:
                writer.writerow([source, ";".join(headers), ";".join(row)])

        QMessageBox.information(self, "Generate Laporan", f"Laporan CSV berhasil dibuat: {csv_path}")


class UserDashboardScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self, username="User"):
        super().__init__()
        self.ui = Ui_DashboardUserUI()
        self.ui.setupUi(self)
        self.username = username
        # connect logout if exists
        if hasattr(self.ui, "btnLogout"):
            self.ui.btnLogout.clicked.connect(self.switch_to_welcome.emit)
        # connect view/unggah bukti buttons if present
        if hasattr(self.ui, "btnViewPaymentProof"):
            self.ui.btnViewPaymentProof.clicked.connect(lambda: QMessageBox.information(self, "Info", "Fungsi belum diimplementasikan."))


class TambahKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_TambahKamarForm()
        self.ui.setupUi(self)
        # connect tambah
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self._handle_tambah)
        # connect pilih gambar
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self._pilih_gambar)
        # connect kembali
        if hasattr(self.ui, "pushButton_2"):
            self.ui.pushButton_2.clicked.connect(self.back_to_dashboard.emit)

    def _handle_tambah(self):
        nama = getattr(self.ui, "input_nama", None)
        if nama is not None and nama.text().strip():
            QMessageBox.information(self, "Berhasil", f"Kamar '{nama.text().strip()}' berhasil ditambahkan.")
            self.back_to_dashboard.emit()
        else:
            QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")

    def _pilih_gambar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path and hasattr(self.ui, "lineEdit"):
            self.ui.lineEdit.setText(path)


class EditKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_EditKamarForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self._handle_edit)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self._pilih_gambar)
        if hasattr(self.ui, "pushButton_2"):
            self.ui.pushButton_2.clicked.connect(self.back_to_dashboard.emit)

    def _handle_edit(self):
        nama = getattr(self.ui, "input_nama", None)
        if nama is not None and nama.text().strip():
            QMessageBox.information(self, "Berhasil", f"Kamar '{nama.text().strip()}' berhasil diupdate.")
            self.back_to_dashboard.emit()
        else:
            QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")

    def _pilih_gambar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path and hasattr(self.ui, "lineEdit"):
            self.ui.lineEdit.setText(path)


class HapusKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_HapusKamarForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self._handle_hapus)
        if hasattr(self.ui, "pushButton_2"):
            self.ui.pushButton_2.clicked.connect(self.back_to_dashboard.emit)

    def _handle_hapus(self):
        nama = getattr(self.ui, "input_nama", None)
        if nama is not None and nama.text().strip():
            reply = QMessageBox.question(self, "Konfirmasi", f"Hapus kamar '{nama.text().strip()}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                QMessageBox.information(self, "Berhasil", "Kamar dihapus.")
                self.back_to_dashboard.emit()
        else:
            QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")


class LihatBuktiScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_LihatBuktiTransfer()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


class KonfirmasiPembayaranScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_KonfirmasiPembayaran()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


class LihatRatingScreen(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DialogDetailUlasan()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.close)


class HapusRatingScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetHapusRating()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


class HapusKritikScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetKritikSaran()
        self.ui.setupUi(self)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


class TolakPembayaranScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        if Ui_TolakPembayaran is None:
            # placeholder widget when UI not available
            super_layout = QtWidgets.QVBoxLayout(self)
            label = QtWidgets.QLabel("Tolak Pembayaran (UI tidak tersedia)")
            btn = QtWidgets.QPushButton("Kembali")
            btn.clicked.connect(self.back_to_dashboard.emit)
            super_layout.addWidget(label); super_layout.addWidget(btn)
        else:
            self.ui = Ui_TolakPembayaran()
            self.ui.setupUi(self)
            if hasattr(self.ui, "pushButton"):
                self.ui.pushButton.clicked.connect(self.back_to_dashboard.emit)


# ---------- MainWindow ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏨 Aplikasi Penginapan Pandawa 🏨")
        self.setGeometry(100, 100, 1000, 700)

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # state
        self.current_username = None
        self.current_role = None  # "admin" or "user"

        # screens
        self.welcome = WelcomeScreen()
        self.login = LoginScreen()
        self.register = RegisterScreen()
        self.admin_dash = None
        self.user_dash = None

        # utility screens (created once)
        self.tambah = TambahKamarScreen()
        self.edit = EditKamarScreen()
        self.hapus_kamar = HapusKamarScreen()
        self.lihat_bukti = LihatBuktiScreen()
        self.konfirmasi = KonfirmasiPembayaranScreen()
        self.lihat_rating = LihatRatingScreen()
        self.hapus_rating = HapusRatingScreen()
        self.hapus_kritik = HapusKritikScreen()
        self.tolak = TolakPembayaranScreen()

        # add always-available screens
        for w in (self.welcome, self.login, self.register,
                  self.tambah, self.edit, self.hapus_kamar,
                  self.lihat_bukti, self.konfirmasi, self.hapus_rating,
                  self.hapus_kritik, self.tolak):
            self.stacked.addWidget(w)

        # connect navigation signals
        self._connect_signals()

        self.stacked.setCurrentWidget(self.welcome)

    def _connect_signals(self):
        # welcome
        self.welcome.switch_to_login.connect(lambda: self.stacked.setCurrentWidget(self.login))
        self.welcome.switch_to_register.connect(lambda: self.stacked.setCurrentWidget(self.register))

        # login/register
        self.login.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))
        self.login.switch_to_dashboard.connect(self.show_dashboard_from_payload)
        self.register.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))

        # utility screens back -> return to dashboard (use stored role)
        for w in (self.tambah, self.edit, self.hapus_kamar,
                  self.lihat_bukti, self.konfirmasi, self.hapus_rating,
                  self.hapus_kritik, self.tolak):
            if hasattr(w, "back_to_dashboard"):
                w.back_to_dashboard.connect(self._show_dashboard_current)

    def show_dashboard_from_payload(self, payload):
        # payload is (username, role)
        username, role = ("", "user")
        if isinstance(payload, tuple) and len(payload) == 2:
            username, role = payload
        elif isinstance(payload, str):
            username = payload
        self.current_username = username or ""
        self.current_role = role or "user"
        # create dashboards lazily
        if role == "admin":
            if self.admin_dash is None:
                self.admin_dash = AdminDashboardScreen(username=self.current_username or "admin")
                # connect admin dashboard signals to show utility screens
                self.admin_dash.show_tambah_kamar.connect(lambda: self.stacked.setCurrentWidget(self.tambah))
                self.admin_dash.show_edit_kamar.connect(lambda: self.stacked.setCurrentWidget(self.edit))
                self.admin_dash.show_hapus_kamar.connect(lambda: self.stacked.setCurrentWidget(self.hapus_kamar))
                self.admin_dash.show_lihat_bukti.connect(lambda: self.stacked.setCurrentWidget(self.lihat_bukti))
                self.admin_dash.show_konfirmasi_pembayaran.connect(lambda: self.stacked.setCurrentWidget(self.konfirmasi))
                self.admin_dash.show_lihat_rating.connect(lambda: self.lihat_rating.show())
                self.admin_dash.show_hapus_rating.connect(lambda: self.stacked.setCurrentWidget(self.hapus_rating))
                self.admin_dash.show_hapus_kritik.connect(lambda: self.stacked.setCurrentWidget(self.hapus_kritik))
                self.admin_dash.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))
                self.stacked.addWidget(self.admin_dash)
            self.stacked.setCurrentWidget(self.admin_dash)
        else:
            if self.user_dash is None:
                self.user_dash = UserDashboardScreen(username=self.current_username or "User")
                # connect user dashboard buttons if any to utility screens
                # example: if UI has btnViewPaymentProof, connect to lihat_bukti
                if hasattr(self.user_dash.ui, "btnViewPaymentProof"):
                    self.user_dash.ui.btnViewPaymentProof.clicked.connect(lambda: self.stacked.setCurrentWidget(self.lihat_bukti))
                if hasattr(self.user_dash.ui, "btnLogout"):
                    self.user_dash.ui.btnLogout.clicked.connect(lambda: self.stacked.setCurrentWidget(self.welcome))
                self.stacked.addWidget(self.user_dash)
            self.stacked.setCurrentWidget(self.user_dash)

    def _show_dashboard_current(self):
        # return to dashboard using stored role
        if self.current_role == "admin":
            if self.admin_dash is not None:
                self.stacked.setCurrentWidget(self.admin_dash)
            else:
                # fallback: show welcome
                self.stacked.setCurrentWidget(self.welcome)
        else:
            if self.user_dash is not None:
                self.stacked.setCurrentWidget(self.user_dash)
            else:
                self.stacked.setCurrentWidget(self.welcome)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Ensure DB connectivity before starting — show Retry/Cancel dialog
    from PyQt5.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)
    while True:
        try:
            conn = connect_db()
            if conn is not None:
                try:
                    conn.ping(reconnect=True, attempts=1, delay=0)
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass
            break
        except Exception as e:
            ret = QMessageBox.critical(None, "Koneksi Database Gagal",
                                       f"Tidak dapat terhubung ke database:\n{e}\n\nPeriksa service MySQL dan kredensial di file database/db_connect.py",
                                       QMessageBox.Retry | QMessageBox.Cancel)
            if ret == QMessageBox.Retry:
                continue
            else:
                sys.exit(1)
    # launch main window
    main()