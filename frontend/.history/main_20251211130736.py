# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QApplication, QMessageBox, QFileDialog

# UI imports
from tampilan_awal import Ui_WelcomeForm
from login import Ui_LoginForm
from register import Ui_RegisterForm
from dashboard_admin import Ui_DashboardAdmin as Ui_DashboardAdminUI

# dashboard_user may not exist in all projects; attempt import
try:
    from dashboard_user import Ui_DashboardAdmin as Ui_DashboardUserUI
except Exception:
    Ui_DashboardUserUI = Ui_DashboardAdminUI  # fallback to admin UI if not available

from tambah import Ui_TambahKamar as Ui_TambahKamarForm
from edit import Ui_TambahKamar as Ui_EditKamarForm
from hapus_kamar import Ui_TambahKamar as Ui_HapusKamarForm
from lihat_bukti_tf import Ui_WidgetDataTransfer as Ui_LihatBuktiTransfer
from konfirmasi_pembayaran import Ui_WidgetDataTransfer as Ui_KonfirmasiPembayaran
from lihat_rating import Ui_DialogDetailUlasan
from hapus_rating import Ui_WidgetHapusRating
from hapus_kritik import Ui_WidgetKritikSaran
# tolak_pembayaran may not be present in attachments; import guarded
try:
    from tolak_pembayaran import Ui_TolakPembayaran
except Exception:
    Ui_TolakPembayaran = None


# ---------- Screens (widgets) ----------

class WelcomeScreen(QtWidgets.QWidget):
    switch_to_login = QtCore.pyqtSignal()
    switch_to_register = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WelcomeForm()
        self.ui.setupUi(self)
        # safe connect
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
        # Simple role decision: username 'admin' -> admin
        role = "admin" if username.lower() in ("admin", "administrator") else "user"
        QMessageBox.information(self, "Login Berhasil", f"Selamat datang {username} ({role})")
        # clear fields
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
            "btnLogout": self.switch_to_welcome
        }
        for name, sig in mapping.items():
            w = getattr(self.ui, name, None)
            if w is not None:
                # if sig is Qt signal, call emit; if switch_to_welcome (signal) then connect to emit
                if isinstance(sig, QtCore.pyqtBoundSignal):
                    w.clicked.connect(sig.emit)
                else:
                    # sig is signal object stored above
                    w.clicked.connect(sig.emit)


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
    main()