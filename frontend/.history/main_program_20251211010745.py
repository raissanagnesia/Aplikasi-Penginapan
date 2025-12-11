# -*- coding: utf-8 -*-

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QApplication

# Import semua UI files
from tampilan_awal import Ui_WelcomeForm
from login import Ui_LoginForm
from register import Ui_RegisterForm
from dashboard_user import Ui_DashboardAdmin
from tambah import Ui_TambahKamar as Ui_TambahKamarForm
from edit import Ui_TambahKamar as Ui_EditKamarForm
from hapus_kamar import Ui_TambahKamar as Ui_HapusKamarForm
from lihat_bukti_tf import Ui_WidgetDataTransfer as Ui_LihatBuktiTransfer
from konfirmasi_pembayaran import Ui_WidgetDataTransfer as Ui_KonfirmasiPembayaran
from lihat_rating import Ui_DialogDetailUlasan
from hapus_rating import Ui_WidgetHapusRating
from hapus_kritik import Ui_WidgetKritikSaran
from tolak_pembayaran import Ui_TolakPembayaran


class WelcomeScreen(QtWidgets.QWidget):
    """Screen Awal - Selamat Datang"""
    switch_to_login = QtCore.pyqtSignal()
    switch_to_register = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_WelcomeForm()
        self.ui.setupUi(self)
        self.connect_buttons()
    
    def connect_buttons(self):
        self.ui.btnLogin.clicked.connect(self.switch_to_login.emit)
        self.ui.btnRegister.clicked.connect(self.switch_to_register.emit)


class LoginScreen(QtWidgets.QWidget):
    """Screen Login"""
    switch_to_welcome = QtCore.pyqtSignal()
    switch_to_dashboard = QtCore.pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        self.connect_buttons()
    
    def connect_buttons(self):
        self.ui.btnLogin.clicked.connect(self.handle_login)
    
    def handle_login(self):
        """Handle login logic"""
        username = self.ui.txtUsername.text()
        password = self.ui.txtPassword.text()
        
        if username and password:
            # TODO: Validasi dengan database
            QtWidgets.QMessageBox.information(self, "Login Berhasil", f"Selamat datang {username}!")
            self.switch_to_dashboard.emit(username)
            # Reset form
            self.ui.txtUsername.clear()
            self.ui.txtPassword.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Login Gagal", "Username dan Password harus diisi!")


class RegisterScreen(QtWidgets.QWidget):
    """Screen Register"""
    switch_to_welcome = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterForm()
        self.ui.setupUi(self)
        self.connect_buttons()
    
    def connect_buttons(self):
        self.ui.btnRegister.clicked.connect(self.handle_register)
    
    def handle_register(self):
        """Handle register logic"""
        username = self.ui.txtUsername.text()
        password = self.ui.txtPassword.text()
        nama = self.ui.txtNama.text()
        email = self.ui.txtEmail.text()
        wa = self.ui.txtWA.text()
        
        if all([username, password, nama, email, wa]):
            # TODO: Simpan ke database
            QtWidgets.QMessageBox.information(self, "Registrasi Berhasil", f"Selamat datang {nama}! Silakan login.")
            self.reset_form()
            self.switch_to_welcome.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Registrasi Gagal", "Semua field harus diisi!")
    
    def reset_form(self):
        self.ui.txtUsername.clear()
        self.ui.txtPassword.clear()
        self.ui.txtNama.clear()
        self.ui.txtEmail.clear()
        self.ui.txtWA.clear()


class DashboardScreen(QtWidgets.QWidget):
    """Screen Dashboard Admin"""
    switch_to_welcome = QtCore.pyqtSignal()
    show_tambah_kamar = QtCore.pyqtSignal()
    show_edit_kamar = QtCore.pyqtSignal()
    show_hapus_kamar = QtCore.pyqtSignal()
    show_lihat_bukti = QtCore.pyqtSignal()
    show_konfirmasi_pembayaran = QtCore.pyqtSignal()
    show_lihat_rating = QtCore.pyqtSignal()
    show_hapus_rating = QtCore.pyqtSignal()
    show_hapus_kritik = QtCore.pyqtSignal()
    
    def __init__(self, username="User"):
        super().__init__()
        self.username = username
        self.ui = Ui_DashboardAdmin()
        self.ui.setupUi(self)
        self.setup_dashboard_buttons()
    
    def setup_dashboard_buttons(self):
        """Setup semua button di dashboard"""
        # Tab Rooms - Button untuk tambah/edit/hapus kamar
        if hasattr(self.ui, 'btnPrice2'):
            self.ui.btnPrice2.clicked.connect(self.show_tambah_kamar.emit)
        
        # Tambahkan koneksi untuk button-button di berbagai tab
        # Anda perlu menyesuaikan dengan nama button yang sebenarnya di dashboard_user.ui
        
        # Contoh untuk buttons yang mungkin ada:
        # if hasattr(self.ui, 'btnTambahKamar'):
        #     self.ui.btnTambahKamar.clicked.connect(self.show_tambah_kamar.emit)


class TambahKamarScreen(QtWidgets.QWidget):
    """Screen Tambah Kamar"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_TambahKamarForm()
        self.ui.setupUi(self)
        self.setup_buttons()
    
    def setup_buttons(self):
        self.ui.btn_tambah.clicked.connect(self.handle_tambah)
        self.ui.pushButton.clicked.connect(self.handle_pilih_gambar)
    
    def handle_tambah(self):
        """Handle tambah kamar"""
        nama = self.ui.input_nama.text()
        deskripsi = self.ui.input_deskripsi.toPlainText()
        stok = self.ui.input_stok.text()
        harga = self.ui.input_harga.text()
        
        if all([nama, deskripsi, stok, harga]):
            # TODO: Simpan ke database
            QtWidgets.QMessageBox.information(self, "Berhasil", f"Kamar '{nama}' berhasil ditambahkan!")
            self.reset_form()
            self.back_to_dashboard.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Gagal", "Semua field harus diisi!")
    
    def handle_pilih_gambar(self):
        """Handle pilih gambar"""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Pilih Gambar Kamar", "", "Image Files (*.jpg *.png *.bmp)")
        if file_path:
            self.ui.lineEdit.setText(file_path)
    
    def reset_form(self):
        self.ui.input_nama.clear()
        self.ui.input_deskripsi.clear()
        self.ui.input_stok.clear()
        self.ui.input_harga.clear()
        self.ui.lineEdit.setText("Pilih gambar kamar")


class EditKamarScreen(QtWidgets.QWidget):
    """Screen Edit Kamar"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_EditKamarForm()
        self.ui.setupUi(self)
        self.setup_buttons()
    
    def setup_buttons(self):
        self.ui.btn_tambah.clicked.connect(self.handle_edit)
        self.ui.pushButton.clicked.connect(self.handle_pilih_gambar)
    
    def handle_edit(self):
        """Handle edit kamar"""
        nama = self.ui.input_nama.text()
        deskripsi = self.ui.input_deskripsi.toPlainText()
        stok = self.ui.input_stok.text()
        harga = self.ui.input_harga.text()
        
        if all([nama, deskripsi, stok, harga]):
            # TODO: Update ke database
            QtWidgets.QMessageBox.information(self, "Berhasil", f"Kamar '{nama}' berhasil diperbarui!")
            self.reset_form()
            self.back_to_dashboard.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Gagal", "Semua field harus diisi!")
    
    def handle_pilih_gambar(self):
        """Handle pilih gambar"""
        file_dialog = QtWidgets.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Pilih Gambar Kamar", "", "Image Files (*.jpg *.png *.bmp)")
        if file_path:
            self.ui.lineEdit.setText(file_path)
    
    def reset_form(self):
        self.ui.input_nama.clear()
        self.ui.input_deskripsi.clear()
        self.ui.input_stok.clear()
        self.ui.input_harga.clear()
        self.ui.lineEdit.setText("Pilih gambar kamar")


class HapusKamarScreen(QtWidgets.QWidget):
    """Screen Hapus Kamar"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_HapusKamarForm()
        self.ui.setupUi(self)
        self.setup_buttons()
    
    def setup_buttons(self):
        self.ui.btn_tambah.clicked.connect(self.handle_hapus)
    
    def handle_hapus(self):
        """Handle hapus kamar"""
        nama = self.ui.input_nama.text()
        
        if nama:
            reply = QtWidgets.QMessageBox.question(
                self, "Konfirmasi Hapus", 
                f"Anda yakin ingin menghapus kamar '{nama}'?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                # TODO: Hapus dari database
                QtWidgets.QMessageBox.information(self, "Berhasil", f"Kamar '{nama}' berhasil dihapus!")
                self.reset_form()
                self.back_to_dashboard.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Gagal", "Nama kamar harus diisi!")
    
    def reset_form(self):
        self.ui.input_nama.clear()
        self.ui.input_deskripsi.clear()
        self.ui.input_stok.clear()
        self.ui.input_harga.clear()


class LihatBuktiScreen(QtWidgets.QWidget):
    """Screen Lihat Bukti Transfer"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_LihatBuktiTransfer()
        self.ui.setupUi(self)


class KonfirmasiPembayaranScreen(QtWidgets.QWidget):
    """Screen Konfirmasi Pembayaran"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_KonfirmasiPembayaran()
        self.ui.setupUi(self)


class LihatRatingScreen(QtWidgets.QDialog):
    """Screen Lihat Rating"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_DialogDetailUlasan()
        self.ui.setupUi(self)


class HapusRatingScreen(QtWidgets.QWidget):
    """Screen Hapus Rating"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetHapusRating()
        self.ui.setupUi(self)


class HapusKritikScreen(QtWidgets.QWidget):
    """Screen Hapus Kritik"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_WidgetKritikSaran()
        self.ui.setupUi(self)


class TolakPembayaranScreen(QtWidgets.QWidget):
    """Screen Tolak Pembayaran"""
    back_to_dashboard = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_TolakPembayaran()
        self.ui.setupUi(self)


class MainWindow(QMainWindow):
    """Main Window - Aplikasi Utama"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏨 Aplikasi Penginapan Pandawa 🏨")
        self.setGeometry(100, 100, 1000, 700)
        
        # Stacked Widget untuk menampung semua screen
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Inisialisasi semua screen
        self.welcome_screen = WelcomeScreen()
        self.login_screen = LoginScreen()
        self.register_screen = RegisterScreen()
        self.dashboard_screen = None
        
        self.tambah_kamar_screen = TambahKamarScreen()
        self.edit_kamar_screen = EditKamarScreen()
        self.hapus_kamar_screen = HapusKamarScreen()
        self.lihat_bukti_screen = LihatBuktiScreen()
        self.konfirmasi_pembayaran_screen = KonfirmasiPembayaranScreen()
        self.lihat_rating_screen = LihatRatingScreen()
        self.hapus_rating_screen = HapusRatingScreen()
        self.hapus_kritik_screen = HapusKritikScreen()
        self.tolak_pembayaran_screen = TolakPembayaranScreen()
        
        # Tambahkan semua screen ke stacked widget
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.register_screen)
        self.stacked_widget.addWidget(self.tambah_kamar_screen)
        self.stacked_widget.addWidget(self.edit_kamar_screen)
        self.stacked_widget.addWidget(self.hapus_kamar_screen)
        self.stacked_widget.addWidget(self.lihat_bukti_screen)
        self.stacked_widget.addWidget(self.konfirmasi_pembayaran_screen)
        self.stacked_widget.addWidget(self.hapus_rating_screen)
        self.stacked_widget.addWidget(self.hapus_kritik_screen)
        self.stacked_widget.addWidget(self.tolak_pembayaran_screen)
        
        # Connect signals untuk navigasi
        self.connect_signals()
        
        # Tampilkan welcome screen terlebih dahulu
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
    
    def connect_signals(self):
        """Connect semua signal navigasi"""
        
        # Welcome Screen
        self.welcome_screen.switch_to_login.connect(self.show_login)
        self.welcome_screen.switch_to_register.connect(self.show_register)
        
        # Login Screen
        self.login_screen.switch_to_welcome.connect(self.show_welcome)
        self.login_screen.switch_to_dashboard.connect(self.show_dashboard)
        
        # Register Screen
        self.register_screen.switch_to_welcome.connect(self.show_welcome)
        
        # Tambah Kamar Screen
        self.tambah_kamar_screen.back_to_dashboard.connect(self.show_dashboard)
        
        # Edit Kamar Screen
        self.edit_kamar_screen.back_to_dashboard.connect(self.show_dashboard)
        
        # Hapus Kamar Screen
        self.hapus_kamar_screen.back_to_dashboard.connect(self.show_dashboard)
        
        # Lihat Bukti Screen
        self.lihat_bukti_screen.back_to_dashboard.connect(self.show_dashboard)
        
        # Konfirmasi Pembayaran Screen
        self.konfirmasi_pembayaran_screen.back_to_dashboard.connect(self.show_dashboard)
        
        # Hapus Rating Screen
        self.hapus_rating_screen.back_to_dashboard.connect(self.show_dashboard)
        
        # Hapus Kritik Screen
        self.hapus_kritik_screen.back_to_dashboard.connect(self.show_dashboard)
        
        # Tolak Pembayaran Screen
        self.tolak_pembayaran_screen.back_to_dashboard.connect(self.show_dashboard)
    
    def show_welcome(self):
        """Tampilkan welcome screen"""
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
    
    def show_login(self):
        """Tampilkan login screen"""
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def show_register(self):
        """Tampilkan register screen"""
        self.stacked_widget.setCurrentWidget(self.register_screen)
    
    def show_dashboard(self, username="User"):
        """Tampilkan dashboard screen"""
        if self.dashboard_screen is None:
            self.dashboard_screen = DashboardScreen(username)
            
            # Connect dashboard buttons ke screen yang sesuai
            self.dashboard_screen.show_tambah_kamar.connect(self.show_tambah_kamar)
            self.dashboard_screen.show_edit_kamar.connect(self.show_edit_kamar)
            self.dashboard_screen.show_hapus_kamar.connect(self.show_hapus_kamar)
            self.dashboard_screen.show_lihat_bukti.connect(self.show_lihat_bukti)
            self.dashboard_screen.show_konfirmasi_pembayaran.connect(self.show_konfirmasi_pembayaran)
            self.dashboard_screen.show_lihat_rating.connect(self.show_lihat_rating)
            self.dashboard_screen.show_hapus_rating.connect(self.show_hapus_rating)
            self.dashboard_screen.show_hapus_kritik.connect(self.show_hapus_kritik)
            
            self.stacked_widget.addWidget(self.dashboard_screen)
        
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)
    
    def show_tambah_kamar(self):
        """Tampilkan tambah kamar screen"""
        self.stacked_widget.setCurrentWidget(self.tambah_kamar_screen)
    
    def show_edit_kamar(self):
        """Tampilkan edit kamar screen"""
        self.stacked_widget.setCurrentWidget(self.edit_kamar_screen)
    
    def show_hapus_kamar(self):
        """Tampilkan hapus kamar screen"""
        self.stacked_widget.setCurrentWidget(self.hapus_kamar_screen)
    
    def show_lihat_bukti(self):
        """Tampilkan lihat bukti screen"""
        self.stacked_widget.setCurrentWidget(self.lihat_bukti_screen)
    
    def show_konfirmasi_pembayaran(self):
        """Tampilkan konfirmasi pembayaran screen"""
        self.stacked_widget.setCurrentWidget(self.konfirmasi_pembayaran_screen)
    
    def show_lihat_rating(self):
        """Tampilkan lihat rating screen"""
        self.lihat_rating_screen.show()
    
    def show_hapus_rating(self):
        """Tampilkan hapus rating screen"""
        self.stacked_widget.setCurrentWidget(self.hapus_rating_screen)
    
    def show_hapus_kritik(self):
        """Tampilkan hapus kritik screen"""
        self.stacked_widget.setCurrentWidget(self.hapus_kritik_screen)
    
    def show_tolak_pembayaran(self):
        """Tampilkan tolak pembayaran screen"""
        self.stacked_widget.setCurrentWidget(self.tolak_pembayaran_screen)


def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()