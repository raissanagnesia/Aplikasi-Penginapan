# ...existing code...
# -*- coding: utf-8 -*-
import sys
import os
import csv
from datetime import datetime
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox, QFileDialog, QPushButton, QTableWidgetItem
)
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument

# UI imports (existing generated UI modules in your frontend folder)
from tampilan_awal import Ui_WelcomeForm
from login import Ui_LoginForm
from register import Ui_RegisterForm
from dashboard_admin import Ui_DashboardAdmin as Ui_DashboardAdminUI

# Try user dashboard UI, fallback to admin UI if missing
try:
    from dashboard_user import Ui_DashboardAdmin as Ui_DashboardUserUI
except Exception:
    Ui_DashboardUserUI = Ui_DashboardAdminUI

# Other UI modules (may be empty but kept for navigation)
from tambah import Ui_TambahKamar as Ui_TambahKamarForm
from edit import Ui_TambahKamar as Ui_EditKamarForm
from hapus_kamar import Ui_TambahKamar as Ui_HapusKamarForm
from lihat_bukti_tf import Ui_WidgetDataTransfer as Ui_LihatBuktiTransfer
from konfirmasi_pembayaran import Ui_WidgetDataTransfer as Ui_KonfirmasiPembayaran
from lihat_rating import Ui_DialogDetailUlasan
from hapus_rating import Ui_WidgetHapusRating
from hapus_kritik import Ui_WidgetKritikSaran
try:
    from tolak_pembayaran import Ui_TolakPembayaran
except Exception:
    Ui_TolakPembayaran = None

# ---------- Screens ----------

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
        role = "admin" if username.lower() in ("admin", "administrator") else "user"
        QMessageBox.information(self, "Login Berhasil", f"Selamat datang {username} ({role})")
        if uname is not None: uname.clear()
        if pwd is not None: pwd.clear()
        self.switch_to_dashboard.emit((username, role))

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
        for name in ("txtUsername","txtPassword","txtNama","txtEmail","txtWA"):
            w = get(name)
            vals.append(w.text().strip() if w is not None else "")
        if not all(vals):
            QMessageBox.warning(self, "Registrasi Gagal", "Semua field harus diisi!")
            return
        QMessageBox.information(self, "Registrasi Berhasil", f"Selamat datang {vals[2]}! Silakan login.")
        for name in ("txtUsername","txtPassword","txtNama","txtEmail","txtWA"):
            w = getattr(self.ui, name, None)
            if w is not None: w.clear()
        self.switch_to_welcome.emit()

# ---------- Admin Dashboard wrapper with robust buttons and features ----------

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
        # ensure header layout exists (dashboard_admin.ui defines frameHeader.horizontalLayout)
        self._ensure_buttons()
        self._connect_default_buttons()

    def _ensure_buttons(self):
        """
        Ensure Refresh / Export PDF / Generate Report buttons exist.
        If not present in UI, create them and add to frameHeader's layout.
        """
        # find existing by attribute or by objectName
        def find_btn(name):
            b = getattr(self.ui, name, None)
            if isinstance(b, QPushButton):
                return b
            # try searching in widget tree
            found = self.findChild(QPushButton, name)
            if isinstance(found, QPushButton):
                return found
            return None

        # header layout target: try common places
        header_layout = None
        if hasattr(self.ui, "frameHeader") and hasattr(self.ui.frameHeader, "layout"):
            header_layout = getattr(self.ui.frameHeader, "layout")() if callable(getattr(self.ui.frameHeader, "layout")) else self.ui.frameHeader.layout()
        if header_layout is None:
            # fallback: try to find horizontalLayout attribute on UI
            header_layout = getattr(self.ui, "horizontalLayout", None)

        # create buttons list: (attr_name, display_text, objectName)
        required = [
            ("btnRefreshData", "Refresh Data", "btnRefreshData"),
            ("btnExportPdf", "Export PDF", "btnExportPdf"),
            ("btnGenerateReport", "Generate Laporan", "btnGenerateReport"),
        ]
        for attr, text, objname in required:
            btn = find_btn(attr)
            if btn is None:
                # create new button and attach to UI object for future reference
                btn = QPushButton(text, self)
                btn.setObjectName(objname)
                setattr(self.ui, attr, btn)  # attach so other code can use getattr(self.ui, attr)
                # add to header layout if available
                if header_layout is not None:
                    header_layout.addWidget(btn)
                else:
                    # as last resort add to this widget's layout (vertical)
                    if self.layout() is None:
                        self.setLayout(QtWidgets.QVBoxLayout())
                    self.layout().addWidget(btn)

    def _connect_default_buttons(self):
        # connect known UI buttons (if present) to corresponding slots
        if hasattr(self.ui, "btnRefreshData"):
            try:
                self.ui.btnRefreshData.clicked.connect(self.refresh_data)
            except Exception:
                pass
        if hasattr(self.ui, "btnExportPdf"):
            try:
                self.ui.btnExportPdf.clicked.connect(self.export_pdf)
            except Exception:
                pass
        if hasattr(self.ui, "btnGenerateReport"):
            try:
                self.ui.btnGenerateReport.clicked.connect(self.generate_laporan)
            except Exception:
                pass
        # other navigation buttons if exist
        if hasattr(self.ui, "btnAddRoom"):
            self.ui.btnAddRoom.clicked.connect(self.show_tambah_kamar.emit)
        if hasattr(self.ui, "btnEditRoom"):
            self.ui.btnEditRoom.clicked.connect(self.show_edit_kamar.emit)
        if hasattr(self.ui, "btnDeleteRoom"):
            self.ui.btnDeleteRoom.clicked.connect(self.show_hapus_kamar.emit)
        if hasattr(self.ui, "btnLogout"):
            self.ui.btnLogout.clicked.connect(self.switch_to_welcome.emit)

    # ---------- feature implementations ----------

    def _find_any_table(self):
        """
        Return first QTableWidget found in UI (search attributes and children).
        """
        # search attributes on ui
        for v in self.ui.__dict__.values():
            if isinstance(v, QtWidgets.QTableWidget):
                return v
        # search child widgets
        found = self.findChild(QtWidgets.QTableWidget)
        if found is not None:
            return found
        # no table found
        return None

    def refresh_data(self):
        """
        Refresh tables in the UI by setting placeholder content.
        Replace with your data reload logic.
        """
        found_any = False
        # scan attributes for QTableWidget
        for name, val in self.ui.__dict__.items():
            if isinstance(val, QtWidgets.QTableWidget):
                table = val
                table.clearContents()
                table.setRowCount(1)
                cols = table.columnCount() or 1
                for c in range(cols):
                    table.setItem(0, c, QTableWidgetItem(f"Refreshed {name} c{c+1}"))
                found_any = True
        # scan child widgets as fallback
        if not found_any:
            for t in self.findChildren(QtWidgets.QTableWidget):
                t.clearContents()
                t.setRowCount(1)
                cols = t.columnCount() or 1
                for c in range(cols):
                    t.setItem(0, c, QTableWidgetItem(f"Refreshed table c{c+1}"))
                found_any = True
        if found_any:
            QMessageBox.information(self, "Refresh Data", "Data berhasil direfresh (placeholder).")
        else:
            QMessageBox.information(self, "Refresh Data", "Tidak ditemukan tabel untuk direfresh di UI.")

    def _table_to_html(self, table):
        rows = table.rowCount()
        cols = table.columnCount()
        # headers
        headers = []
        for c in range(cols):
            hi = table.horizontalHeaderItem(c)
            headers.append(hi.text() if hi is not None else f"Col{c+1}")
        html = "<table border='1' cellpadding='4' cellspacing='0'>"
        html += "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
        for r in range(rows):
            html += "<tr>"
            for c in range(cols):
                it = table.item(r, c)
                html += f"<td>{it.text() if it is not None else ''}</td>"
            html += "</tr>"
        html += "</table>"
        return html

    def export_pdf(self):
        """
        Export first available table to PDF. Uses QTextDocument + QPrinter.
        """
        table = None
        # prefer attribute tables
        for v in self.ui.__dict__.values():
            if isinstance(v, QtWidgets.QTableWidget):
                table = v
                break
        if table is None:
            # try findChild
            table = self.findChild(QtWidgets.QTableWidget)
        if table is None:
            QMessageBox.warning(self, "Export PDF", "Tidak ditemukan tabel untuk diexport.")
            return

        fname, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", os.path.expanduser("~/laporan.pdf"), "PDF files (*.pdf)")
        if not fname:
            return

        html = f"<h2>Laporan - {self.username} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>"
        html += self._table_to_html(table)
        doc = QTextDocument()
        doc.setHtml(html)
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(fname)
        doc.print_(printer)
        QMessageBox.information(self, "Export PDF", f"PDF berhasil disimpan: {fname}")

    def generate_laporan(self):
        """
        Generate a simple CSV report collecting rows from existing tables.
        """
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join("reports", f"laporan_{timestamp}.csv")
        collected = []
        # collect from attribute tables
        for name, val in self.ui.__dict__.items():
            if isinstance(val, QtWidgets.QTableWidget):
                headers = [val.horizontalHeaderItem(c).text() if val.horizontalHeaderItem(c) is not None else f"Col{c+1}" for c in range(val.columnCount())]
                for r in range(val.rowCount()):
                    row = [val.item(r, c).text() if val.item(r, c) is not None else "" for c in range(val.columnCount())]
                    collected.append((name, headers, row))
        if not collected:
            QMessageBox.information(self, "Generate Laporan", "Tidak ada data tabel untuk dibuat laporan.")
            return
        with open(csv_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["sumber_tabel", "headers", "nilai"])
            for source, headers, row in collected:
                writer.writerow([source, ";".join(headers), ";".join(row)])
        QMessageBox.information(self, "Generate Laporan", f"Laporan CSV berhasil dibuat: {csv_path}")

# ---------- Simple User Dashboard wrapper ----------
class UserDashboardScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()
    def __init__(self, username="User"):
        super().__init__()
        self.ui = Ui_DashboardUserUI()
        self.ui.setupUi(self)
        self.username = username
        if hasattr(self.ui, "btnLogout"):
            self.ui.btnLogout.clicked.connect(self.switch_to_welcome.emit)

# ---------- Placeholder screens for other UI files ----------
class PlaceholderScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()
    def __init__(self, ui_cls):
        super().__init__()
        self.ui = ui_cls()
        try:
            self.ui.setupUi(self)
        except Exception:
            # safe fallback
            layout = QtWidgets.QVBoxLayout(self)
            layout.addWidget(QtWidgets.QLabel("Placeholder UI"))
        # try connect a 'btnBack' or generic button to back
        for name in ("pushButton_2","btnBack","btnKembali"):
            b = getattr(self.ui, name, None)
            if isinstance(b, QPushButton):
                b.clicked.connect(self.back_to_dashboard.emit)

# instantiate utility screens (create as placeholders if UI classes empty)
try:
    tambah_ui = Ui_TambahKamarForm
except Exception:
    tambah_ui = None
try:
    edit_ui = Ui_EditKamarForm
except Exception:
    edit_ui = None
try:
    hapus_ui = Ui_HapusKamarForm
except Exception:
    hapus_ui = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏨 Aplikasi Penginapan Pandawa 🏨")
        self.setGeometry(100,100,1000,700)
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # basic screens
        self.welcome = WelcomeScreen()
        self.login = LoginScreen()
        self.register = RegisterScreen()

        # dashboards (created lazily)
        self.admin_dash = None
        self.user_dash = None
        self.current_role = None
        self.current_username = None

        # utility screens
        self.tambah = PlaceholderScreen(tambah_ui) if tambah_ui is not None else PlaceholderScreen(type("U",(),{"setupUi":lambda s,w:None}))
        self.edit = PlaceholderScreen(edit_ui) if edit_ui is not None else PlaceholderScreen(type("U",(),{"setupUi":lambda s,w:None}))
        self.hapus_kamar = PlaceholderScreen(hapus_ui) if hapus_ui is not None else PlaceholderScreen(type("U",(),{"setupUi":lambda s,w:None}))
        self.lihat_bukti = PlaceholderScreen(Ui_LihatBuktiTransfer)
        self.konfirmasi = PlaceholderScreen(Ui_KonfirmasiPembayaran)
        self.lihat_rating = PlaceholderScreen(Ui_DialogDetailUlasan)
        self.hapus_rating = PlaceholderScreen(Ui_WidgetHapusRating)
        self.hapus_kritik = PlaceholderScreen(Ui_WidgetKritikSaran)
        # tolak
        if Ui_TolakPembayaran is None:
            self.tolak = PlaceholderScreen(type("U",(),{"setupUi":lambda s,w:None}))
        else:
            self.tolak = PlaceholderScreen(Ui_TolakPembayaran)

        # add base widgets
        for w in (self.welcome, self.login, self.register,
                  self.tambah, self.edit, self.hapus_kamar,
                  self.lihat_bukti, self.konfirmasi, self.lihat_rating,
                  self.hapus_rating, self.hapus_kritik, self.tolak):
            self.stacked.addWidget(w)

        # connect navigation
        self.welcome.switch_to_login.connect(lambda: self.stacked.setCurrentWidget(self.login))
        self.welcome.switch_to_register.connect(lambda: self.stacked.setCurrentWidget(self.register))
        self.login.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))
        self.login.switch_to_dashboard.connect(self._show_dashboard)
        self.register.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))

        # utility back signals
        for w in (self.tambah, self.edit, self.hapus_kamar, self.lihat_bukti,
                  self.konfirmasi, self.lihat_rating, self.hapus_rating,
                  self.hapus_kritik, self.tolak):
            if hasattr(w, "back_to_dashboard"):
                w.back_to_dashboard.connect(self._return_to_dashboard)

        self.stacked.setCurrentWidget(self.welcome)

    def _show_dashboard(self, payload):
        username, role = ("", "user")
        if isinstance(payload, tuple) and len(payload) == 2:
            username, role = payload
        elif isinstance(payload, str):
            username = payload
        self.current_username = username
        self.current_role = role
        if role == "admin":
            if self.admin_dash is None:
                self.admin_dash = AdminDashboardScreen(username=username or "admin")
                # connect admin navigation to utility screens
                self.admin_dash.show_tambah_kamar.connect(lambda: self.stacked.setCurrentWidget(self.tambah))
                self.admin_dash.show_edit_kamar.connect(lambda: self.stacked.setCurrentWidget(self.edit))
                self.admin_dash.show_hapus_kamar.connect(lambda: self.stacked.setCurrentWidget(self.hapus_kamar))
                self.admin_dash.show_lihat_bukti.connect(lambda: self.stacked.setCurrentWidget(self.lihat_bukti))
                self.admin_dash.show_konfirmasi_pembayaran.connect(lambda: self.stacked.setCurrentWidget(self.konfirmasi))
                self.admin_dash.show_lihat_rating.connect(lambda: self.stacked.setCurrentWidget(self.lihat_rating))
                self.admin_dash.show_hapus_rating.connect(lambda: self.stacked.setCurrentWidget(self.hapus_rating))
                self.admin_dash.show_hapus_kritik.connect(lambda: self.stacked.setCurrentWidget(self.hapus_kritik))
                self.admin_dash.switch_to_welcome.connect(lambda: self.stacked.setCurrentWidget(self.welcome))
                self.stacked.addWidget(self.admin_dash)
            self.stacked.setCurrentWidget(self.admin_dash)
        else:
            if self.user_dash is None:
                self.user_dash = UserDashboardScreen(username=username or "User")
                if hasattr(self.user_dash.ui, "btnLogout"):
                    self.user_dash.ui.btnLogout.clicked.connect(lambda: self.stacked.setCurrentWidget(self.welcome))
                self.stacked.addWidget(self.user_dash)
            self.stacked.setCurrentWidget(self.user_dash)

    def _return_to_dashboard(self):
        if self.current_role == "admin" and self.admin_dash is not None:
            self.stacked.setCurrentWidget(self.admin_dash)
        elif self.current_role == "user" and self.user_dash is not None:
            self.stacked.setCurrentWidget(self.user_dash)
        else:
            self.stacked.setCurrentWidget(self.welcome)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
# ...existing code...