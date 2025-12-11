# -*- coding: utf-8 -*-

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QApplication

# Import semua UI files
from tampilan_awal import Ui_WelcomeForm
from login import Ui_LoginForm
from register import Ui_RegisterForm

# Dashboard UI: coba import dashboard user UI terlebih dahulu, jika tidak ada fallback ke dashboard_admin
try:
    from dashboard_user import Ui_DashboardAdmin as Ui_DashboardUser  # jika file dashboard_user.py ada
except Exception:
    from dashboard_admin import Ui_DashboardAdmin as Ui_DashboardUser  # fallback

from dashboard_admin import Ui_DashboardAdmin as Ui_DashboardAdminUI
from tambah import Ui_TambahKamar as Ui_TambahKamarForm
from edit import Ui_TambahKamar as Ui_EditKamarForm
from hapus_kamar import Ui_TambahKamar as Ui_HapusKamarForm
from lihat_bukti_tf import Ui_WidgetDataTransfer as Ui_LihatBuktiTransfer
from konfirmasi_pembayaran import Ui_WidgetDataTransfer as Ui_KonfirmasiPembayaran
from lihat_rating import Ui_DialogDetailUlasan
from hapus_rating import Ui_WidgetHapusRating
from hapus_kritik import Ui_WidgetKritikSaran



class WelcomeScreen(QtWidgets.QWidget):
    switch_to_login = QtCore.pyqtSignal()
    switch_to_register = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WelcomeForm()
        self.ui.setupUi(self)
        self.connect_buttons()

    def connect_buttons(self):
        if hasattr(self.ui, "btnLogin"):
            self.ui.btnLogin.clicked.connect(self.switch_to_login.emit)
        if hasattr(self.ui, "btnRegister"):
            self.ui.btnRegister.clicked.connect(self.switch_to_register.emit)


class LoginScreen(QtWidgets.QWidget):
    # emit (username, role) as object
    switch_to_welcome = QtCore.pyqtSignal()
    switch_to_dashboard = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        self.connect_buttons()

    def connect_buttons(self):
        if hasattr(self.ui, "btnLogin"):
            self.ui.btnLogin.clicked.connect(self.handle_login)

    def handle_login(self):
        username = getattr(self.ui, "txtUsername", None)
        password = getattr(self.ui, "txtPassword", None)
        uname = username.text() if username is not None else ""
        pwd = password.text() if password is not None else ""

        if uname and pwd:
            # sederhana: username "admin" dianggap admin
            role = "admin" if uname.strip().lower() in ("admin", "administrator") else "user"
            QtWidgets.QMessageBox.information(self, "Login Berhasil", f"Selamat datang {uname} ({role})!")
            # emit tuple (username, role)
            self.switch_to_dashboard.emit((uname, role))
            if username is not None:
                username.clear()
            if password is not None:
                password.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Login Gagal", "Username dan Password harus diisi!")


class RegisterScreen(QtWidgets.QWidget):
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterForm()
        self.ui.setupUi(self)
        self.connect_buttons()

    def connect_buttons(self):
        if hasattr(self.ui, "btnRegister"):
            self.ui.btnRegister.clicked.connect(self.handle_register)

    def handle_register(self):
        get = lambda name: getattr(self.ui, name, None)
        username = get("txtUsername")
        password = get("txtPassword")
        nama = get("txtNama")
        email = get("txtEmail")
        wa = get("txtWA")
        vals = [w.text() if w is not None else "" for w in (username, password, nama, email, wa)]

        if all(vals):
            QtWidgets.QMessageBox.information(self, "Registrasi Berhasil", f"Selamat datang {vals[2]}! Silakan login.")
            self.reset_form()
            self.switch_to_welcome.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Registrasi Gagal", "Semua field harus diisi!")

    def reset_form(self):
        for name in ("txtUsername", "txtPassword", "txtNama", "txtEmail", "txtWA"):
            w = getattr(self.ui, name, None)
            if w is not None:
                w.clear()


class AdminDashboardScreen(QtWidgets.QWidget):
    """Dashboard untuk admin - menggunakan UI admin"""
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
        self.setup_connections()

    def setup_connections(self):
        # contoh: hubungkan tombol yang ada di dashboard admin ke sinyal
        if hasattr(self.ui, "btnAddRoom"):
            self.ui.btnAddRoom.clicked.connect(self.show_tambah_kamar.emit)
        if hasattr(self.ui, "btnEditRoom"):
            self.ui.btnEditRoom.clicked.connect(self.show_edit_kamar.emit)
        if hasattr(self.ui, "btnDeleteRoom"):
            self.ui.btnDeleteRoom.clicked.connect(self.show_hapus_kamar.emit)
        if hasattr(self.ui, "btnViewPaymentProof"):
            self.ui.btnViewPaymentProof.clicked.connect(self.show_lihat_bukti.emit)
        if hasattr(self.ui, "btnValidatePayment"):
            self.ui.btnValidatePayment.clicked.connect(self.show_konfirmasi_pembayaran.emit)
        if hasattr(self.ui, "btnViewRoomRatings"):
            self.ui.btnViewRoomRatings.clicked.connect(self.show_lihat_rating.emit)
        if hasattr(self.ui, "btnDeleteRating"):
            self.ui.btnDeleteRating.clicked.connect(self.show_hapus_rating.emit)
        if hasattr(self.ui, "btnDeleteFeedback"):
            self.ui.btnDeleteFeedback.clicked.connect(self.show_hapus_kritik.emit)
        if hasattr(self.ui, "btnLogout"):
            self.ui.btnLogout.clicked.connect(self.switch_to_welcome.emit)


class UserDashboardScreen(QtWidgets.QWidget):
    """Dashboard untuk pengunjung/user - menggunakan dashboard_user UI if available"""
    switch_to_welcome = QtCore.pyqtSignal()

    def __init__(self, username="User"):
        super().__init__()
        # Ui_DashboardUser may actually be the same class as admin UI if fallback was used
        self.ui = Ui_DashboardUser()
        self.ui.setupUi(self)
        self.username = username
        self.setup_connections()

    def setup_connections(self):
        # contoh minimal: jika ada tombol logout di UI gunakan itu
        if hasattr(self.ui, "btnLogout"):
            self.ui.btnLogout.clicked.connect(self.switch_to_welcome.emit)
        # jika ada tombol untuk melihat/unggah bukti, hubungkan sesuai nama
        if hasattr(self.ui, "btnViewPaymentProof"):
            self.ui.btnViewPaymentProof.clicked.connect(lambda: QtWidgets.QMessageBox.information(self, "Info", "Lihat bukti (belum diimplementasikan)."))


class TambahKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_TambahKamarForm()
        self.ui.setupUi(self)
        # safe-connect jika widget ada
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self.handle_tambah)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.handle_pilih_gambar)

    def handle_tambah(self):
        get = lambda n: getattr(self.ui, n, None)
        nama = get("input_nama")
        deskripsi = get("input_deskripsi")
        stok = get("input_stok")
        harga = get("input_harga")
        vals = [w.text() if hasattr(w, "text") else (w.toPlainText() if hasattr(w, "toPlainText") else "") for w in (nama, deskripsi, stok, harga)]
        if all(vals):
            QtWidgets.QMessageBox.information(self, "Berhasil", f"Kamar '{vals[0]}' berhasil ditambahkan!")
            self.back_to_dashboard.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Gagal", "Semua field harus diisi!")

    def handle_pilih_gambar(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Pilih Gambar Kamar", "", "Image Files (*.jpg *.png *.bmp)")
        if file_path and hasattr(self.ui, "lineEdit"):
            self.ui.lineEdit.setText(file_path)


class EditKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_EditKamarForm()
        self.ui.setupUi(self)
        if hasattr(self.ui, "btn_tambah"):
            self.ui.btn_tambah.clicked.connect(self.handle_edit)
        if hasattr(self.ui, "pushButton"):
            self.ui.pushButton.clicked.connect(self.handle_pilih_gambar)

    def handle_edit(self):
        get = lambda n: getattr(self.ui, n, None)
        nama = get("input_nama")
        deskripsi = get("input_deskripsi")
        stok = get("input_stok")
        harga = get("input_harga")
        vals = [w.text() if hasattr(w, "text") else (w.toPlainText() if hasattr(w, "toPlainText") else "") for w in (nama, deskripsi, stok, harga)]
        if all(vals):
            QtWidgets.QMessageBox.information(self, "Berhasil", f"Kamar '{vals[0]}' berhasil diperbarui!")
            self.back_to_dashboard.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Gagal", "Semua field harus diisi!")

    def handle_pilih_gambar(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Pilih Gambar Kamar", "", "Image Files (*.jpg *.png *.bmp)")
        if file_path and hasattr(self.ui, "lineEdit"):
            self.ui.lineEdit.setText(file_path)


class HapusKamarScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_HapusKamarForm()
        self.ui.setupUi(self)

    def handle_hapus(self):
        if hasattr(self.ui, "input_nama"):
            nama = self.ui.input_nama.text()
            if nama:
                reply = QtWidgets.QMessageBox.question(self, "Konfirmasi Hapus", f"Anda yakin ingin menghapus kamar '{nama}'?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    QtWidgets.QMessageBox.information(self, "Berhasil", f"Kamar '{nama}' berhasil dihapus!")
                    self.back_to_dashboard.emit()
            else:
                QtWidgets.QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")


class LihatBuktiScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_LihatBuktiTransfer()
        self.ui.setupUi(self)


class KonfirmasiPembayaranScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_KonfirmasiPembayaran()
        self.ui.setupUi(self)


class LihatRatingScreen(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DialogDetailUlasan()
        self.ui.setupUi(self)


class HapusRatingScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetHapusRating()
        self.ui.setupUi(self)


class HapusKritikScreen(QtWidgets.QWidget):
    back_to_dashboard = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetKritikSaran()
        self.ui.setupUi(self)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏨 Aplikasi Penginapan Pandawa 🏨")
        self.setGeometry(100, 100, 1000, 700)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # screens
        self.welcome_screen = WelcomeScreen()
        self.login_screen = LoginScreen()
        self.register_screen = RegisterScreen()

        # placeholders for dashboards
        self.admin_dashboard = None
        self.user_dashboard = None

        # utility screens
        self.tambah_kamar_screen = TambahKamarScreen()
        self.edit_kamar_screen = EditKamarScreen()
        self.hapus_kamar_screen = HapusKamarScreen()
        self.lihat_bukti_screen = LihatBuktiScreen()
        self.konfirmasi_pembayaran_screen = KonfirmasiPembayaranScreen()
        self.lihat_rating_screen = LihatRatingScreen()
        self.hapus_rating_screen = HapusRatingScreen()
        self.hapus_kritik_screen = HapusKritikScreen()
        self.tolak_pembayaran_screen = TolakPembayaranScreen()

        # add to stacked
        for w in (self.welcome_screen, self.login_screen, self.register_screen,
                  self.tambah_kamar_screen, self.edit_kamar_screen, self.hapus_kamar_screen,
                  self.lihat_bukti_screen, self.konfirmasi_pembayaran_screen,
                  self.hapus_rating_screen, self.hapus_kritik_screen, self.tolak_pembayaran_screen):
            self.stacked_widget.addWidget(w)

        self.connect_signals()
        self.stacked_widget.setCurrentWidget(self.welcome_screen)

    def connect_signals(self):
        self.welcome_screen.switch_to_login.connect(self.show_login)
        self.welcome_screen.switch_to_register.connect(self.show_register)

        self.login_screen.switch_to_welcome.connect(self.show_welcome)
        self.login_screen.switch_to_dashboard.connect(self.show_dashboard)

        self.register_screen.switch_to_welcome.connect(self.show_welcome)

        self.tambah_kamar_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))
        self.edit_kamar_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))
        self.hapus_kamar_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))
        self.lihat_bukti_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))
        self.konfirmasi_pembayaran_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))
        self.hapus_rating_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))
        self.hapus_kritik_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))
        self.tolak_pembayaran_screen.back_to_dashboard.connect(lambda: self.show_dashboard(("","admin")))

    def show_welcome(self):
        self.stacked_widget.setCurrentWidget(self.welcome_screen)

    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def show_register(self):
        self.stacked_widget.setCurrentWidget(self.register_screen)

    def show_dashboard(self, payload):
        """
        payload expected: (username, role) or username str
        role == "admin" -> admin dashboard
        else -> user dashboard
        """
        username, role = ("", "user")
        if isinstance(payload, tuple) and len(payload) == 2:
            username, role = payload
        elif isinstance(payload, str):
            username = payload

        if role == "admin":
            if self.admin_dashboard is None:
                self.admin_dashboard = AdminDashboardScreen(username=username or "admin")
                # connect admin buttons
                self.admin_dashboard.show_tambah_kamar.connect(self.show_tambah_kamar)
                self.admin_dashboard.show_edit_kamar.connect(self.show_edit_kamar)
                self.admin_dashboard.show_hapus_kamar.connect(self.show_hapus_kamar)
                self.admin_dashboard.show_lihat_bukti.connect(self.show_lihat_bukti)
                self.admin_dashboard.show_konfirmasi_pembayaran.connect(self.show_konfirmasi_pembayaran)
                self.admin_dashboard.show_lihat_rating.connect(lambda: self.lihat_rating_screen.show())
                self.admin_dashboard.show_hapus_rating.connect(self.show_hapus_rating)
                self.admin_dashboard.show_hapus_kritik.connect(self.show_hapus_kritik)
                self.admin_dashboard.switch_to_welcome.connect(self.show_welcome)
                self.stacked_widget.addWidget(self.admin_dashboard)
            self.stacked_widget.setCurrentWidget(self.admin_dashboard)
        else:
            if self.user_dashboard is None:
                self.user_dashboard = UserDashboardScreen(username=username or "User")
                self.user_dashboard.switch_to_welcome.connect(self.show_welcome)
                self.stacked_widget.addWidget(self.user_dashboard)
            self.stacked_widget.setCurrentWidget(self.user_dashboard)

    def show_tambah_kamar(self):
        self.stacked_widget.setCurrentWidget(self.tambah_kamar_screen)

    def show_edit_kamar(self):
        self.stacked_widget.setCurrentWidget(self.edit_kamar_screen)

    def show_hapus_kamar(self):
        self.stacked_widget.setCurrentWidget(self.hapus_kamar_screen)

    def show_lihat_bukti(self):
        self.stacked_widget.setCurrentWidget(self.lihat_bukti_screen)

    def show_konfirmasi_pembayaran(self):
        self.stacked_widget.setCurrentWidget(self.konfirmasi_pembayaran_screen)

    def show_lihat_rating(self):
        self.lihat_rating_screen.show()

    def show_hapus_rating(self):
        self.stacked_widget.setCurrentWidget(self.hapus_rating_screen)

    def show_hapus_kritik(self):
        self.stacked_widget.setCurrentWidget(self.hapus_kritik_screen)

    def show_tolak_pembayaran(self):
        self.stacked_widget.setCurrentWidget(self.tolak_pembayaran_screen)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()