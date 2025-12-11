#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Application untuk Dashboard Admin Penginapan
Menghubungkan semua button dengan window/dialog yang sesuai
"""

import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox

# Import UI files
from dashboard_admin import Ui_DashboardAdmin
from tambah import Ui_TambahKamar as Ui_Tambah
from edit import Ui_TambahKamar as Ui_Edit
from hapus_kamar import Ui_TambahKamar as Ui_Hapus
from lihat_rating import Ui_DialogDetailUlasan
from lihat_bukti_tf import Ui_WidgetDataTransfer as Ui_BuktiTransfer
from konfirmasi_pembayaran import Ui_WidgetDataTransfer as Ui_KonfirmasiPembayaran
from hapus_kritik import Ui_WidgetKritikSaran
from hapus_rating import Ui_WidgetHapusRating


class AdminMainWindow(QtWidgets.QWidget):
    """Main Window untuk Dashboard Admin"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_DashboardAdmin()
        self.ui.setupUi(self)
        
        # Inisialisasi referensi ke window lain
        self.tambah_window = None
        self.edit_window = None
        self.hapus_window = None
        self.rating_dialog = None
        self.bukti_tf_window = None
        self.konfirmasi_payment_window = None
        self.hapus_kritik_window = None
        self.hapus_rating_window = None
        
        # Connect semua button signals
        self.connect_signals()
        
        # Load data awal untuk semua tab
        self.load_all_data()
    
    def connect_signals(self):
        """Menghubungkan semua button dengan fungsinya"""
        
        # ===== TAB MANAJEMEN KAMAR =====
        self.ui.btnAddRoom.clicked.connect(self.open_tambah_kamar)
        self.ui.btnEditRoom.clicked.connect(self.open_edit_kamar)
        self.ui.btnDeleteRoom.clicked.connect(self.open_hapus_kamar)
        self.ui.btnViewRoomRatings.clicked.connect(self.open_lihat_rating)
        
        # ===== TAB VALIDASI PEMBAYARAN =====
        self.ui.btnRefreshPayments.clicked.connect(self.refresh_payments)
        self.ui.btnViewPaymentProof.clicked.connect(self.open_lihat_bukti_tf)
        self.ui.btnValidatePayment.clicked.connect(self.open_konfirmasi_pembayaran)
        
        # ===== TAB DATA PEMESANAN =====
        self.ui.btnRefreshBookings.clicked.connect(self.refresh_bookings)
        
        # ===== TAB LAPORAN =====
        self.ui.btnGenerateReport.clicked.connect(self.generate_report)
        self.ui.btnExportPDF.clicked.connect(self.export_pdf)
        
        # ===== TAB KRITIK DAN SARAN =====
        self.ui.btnRefreshFeedback.clicked.connect(self.refresh_feedback)
        self.ui.btnDeleteFeedback.clicked.connect(self.open_hapus_kritik)
        
        # ===== TAB RATING KAMAR =====
        self.ui.btnRefreshRatings.clicked.connect(self.refresh_ratings)
        self.ui.btnDeleteRating.clicked.connect(self.open_hapus_rating)
        
        # ===== TAB DATA USER =====
        self.ui.btnRefreshUsers.clicked.connect(self.refresh_users)
        
        # ===== TAB LOGOUT =====
        self.ui.btnLogout.clicked.connect(self.logout)
    
    # ========== FUNGSI UNTUK TAB MANAJEMEN KAMAR ==========
    
    def open_tambah_kamar(self):
        """Membuka window Tambah Kamar"""
        self.tambah_window = QtWidgets.QWidget()
        ui = Ui_Tambah()
        ui.setupUi(self.tambah_window)
        
        # TODO: Connect button tambah dengan fungsi save ke database
        # ui.btn_tambah.clicked.connect(self.save_kamar_to_db)
        
        self.tambah_window.show()
    
    def open_edit_kamar(self):
        """Membuka window Edit Kamar"""
        # Cek apakah ada kamar yang dipilih
        # TODO: Implementasi pemilihan kamar dari list/table
        
        self.edit_window = QtWidgets.QWidget()
        ui = Ui_Edit()
        ui.setupUi(self.edit_window)
        
        # TODO: Load data kamar yang dipilih ke form
        # TODO: Connect button edit dengan fungsi update ke database
        
        self.edit_window.show()
    
    def open_hapus_kamar(self):
        """Membuka window Hapus Kamar"""
        self.hapus_window = QtWidgets.QWidget()
        ui = Ui_Hapus()
        ui.setupUi(self.hapus_window)
        
        # TODO: Load data kamar yang akan dihapus
        # TODO: Connect button hapus dengan fungsi delete dari database
        
        self.hapus_window.show()
    
    def open_lihat_rating(self):
        """Membuka dialog Lihat Rating Kamar"""
        self.rating_dialog = QtWidgets.QDialog()
        ui = Ui_DialogDetailUlasan()
        ui.setupUi(self.rating_dialog)
        
        # TODO: Load data rating dari database
        # self.load_rating_data(ui)
        
        self.rating_dialog.exec_()
    
    # ========== FUNGSI UNTUK TAB VALIDASI PEMBAYARAN ==========
    
    def refresh_payments(self):
        """Refresh data pembayaran dari database"""
        try:
            # TODO: Query data pembayaran dari database
            # payments = db.get_all_payments()
            
            # Clear table
            self.ui.tablePayments.setRowCount(0)
            
            # TODO: Populate table dengan data dari database
            # for payment in payments:
            #     self.add_payment_row(payment)
            
            QMessageBox.information(self, "Refresh", "Data pembayaran berhasil di-refresh!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal refresh data: {str(e)}")
    
    def open_lihat_bukti_tf(self):
        """Membuka window Lihat Bukti Transfer"""
        # Cek apakah ada pembayaran yang dipilih
        selected_rows = self.ui.tablePayments.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Peringatan", "Pilih pembayaran terlebih dahulu!")
            return
        
        self.bukti_tf_window = QtWidgets.QWidget()
        ui = Ui_BuktiTransfer()
        ui.setupUi(self.bukti_tf_window)
        
        # TODO: Load data bukti transfer
        # payment_id = self.ui.tablePayments.item(selected_rows[0].row(), 0).text()
        # transfer_data = db.get_transfer_proof(payment_id)
        # ui.load_transfer_data(transfer_data)
        
        self.bukti_tf_window.show()
    
    def open_konfirmasi_pembayaran(self):
        """Membuka window Konfirmasi Pembayaran"""
        # Cek apakah ada pembayaran yang dipilih
        selected_rows = self.ui.tablePayments.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Peringatan", "Pilih pembayaran terlebih dahulu!")
            return
        
        self.konfirmasi_payment_window = QtWidgets.QWidget()
        ui = Ui_KonfirmasiPembayaran()
        ui.setupUi(self.konfirmasi_payment_window)
        
        # TODO: Load data pembayaran yang akan dikonfirmasi
        # payment_id = self.ui.tablePayments.item(selected_rows[0].row(), 0).text()
        # payment_data = db.get_payment_by_id(payment_id)
        # ui.load_transfer_data([payment_data])
        
        self.konfirmasi_payment_window.show()
    
    # ========== FUNGSI UNTUK TAB DATA PEMESANAN ==========
    
    def refresh_bookings(self):
        """Refresh data pemesanan dari database"""
        try:
            # TODO: Query data pemesanan dari database
            # bookings = db.get_all_bookings()
            
            # Clear table
            self.ui.tableBookings.setRowCount(0)
            
            # TODO: Populate table dengan data dari database
            # for booking in bookings:
            #     self.add_booking_row(booking)
            
            QMessageBox.information(self, "Refresh", "Data pemesanan berhasil di-refresh!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal refresh data: {str(e)}")
    
    # ========== FUNGSI UNTUK TAB LAPORAN ==========
    
    def generate_report(self):
        """Generate laporan berdasarkan periode yang dipilih"""
        try:
            start_date = self.ui.dateStartReport.date()
            end_date = self.ui.dateEndReport.date()
            
            # Validasi tanggal
            if start_date > end_date:
                QMessageBox.warning(self, "Peringatan", "Tanggal mulai tidak boleh lebih besar dari tanggal akhir!")
                return
            
            # TODO: Query data laporan dari database berdasarkan periode
            # report_data = db.get_report(start_date, end_date)
            
            # Clear table
            self.ui.tableReports.setRowCount(0)
            
            # TODO: Populate table dan summary
            # self.populate_report_table(report_data)
            # self.update_summary(report_data)
            
            QMessageBox.information(self, "Laporan", "Laporan berhasil di-generate!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal generate laporan: {str(e)}")
    
    def export_pdf(self):
        """Export laporan ke PDF"""
        try:
            # TODO: Implementasi export ke PDF
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 
                "Simpan Laporan PDF", 
                "laporan_pemesanan.pdf", 
                "PDF Files (*.pdf)"
            )
            
            if filename:
                # TODO: Generate PDF dari data table
                # self.generate_pdf_report(filename)
                QMessageBox.information(self, "Export PDF", f"Laporan berhasil disimpan ke {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export PDF: {str(e)}")
    
    # ========== FUNGSI UNTUK TAB KRITIK DAN SARAN ==========
    
    def refresh_feedback(self):
        """Refresh data kritik dan saran dari database"""
        try:
            # TODO: Query data feedback dari database
            # feedbacks = db.get_all_feedbacks()
            
            # Clear table
            self.ui.tableFeedback.setRowCount(0)
            
            # TODO: Populate table dengan data dari database
            # for feedback in feedbacks:
            #     self.add_feedback_row(feedback)
            
            QMessageBox.information(self, "Refresh", "Data kritik dan saran berhasil di-refresh!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal refresh data: {str(e)}")
    
    def open_hapus_kritik(self):
        """Membuka window Hapus Kritik/Saran"""
        self.hapus_kritik_window = QtWidgets.QWidget()
        ui = Ui_WidgetKritikSaran()
        ui.setupUi(self.hapus_kritik_window)
        
        # TODO: Load data kritik dari database
        # kritik_data = db.get_all_kritik()
        # ui.load_kritik_data(kritik_data)
        
        self.hapus_kritik_window.show()
    
    # ========== FUNGSI UNTUK TAB RATING KAMAR ==========
    
    def refresh_ratings(self):
        """Refresh data rating kamar dari database"""
        try:
            # TODO: Query data rating dari database
            # ratings = db.get_all_ratings()
            
            # Clear table
            self.ui.tableRatings.setRowCount(0)
            
            # TODO: Populate table dengan data dari database
            # for rating in ratings:
            #     self.add_rating_row(rating)
            
            QMessageBox.information(self, "Refresh", "Data rating berhasil di-refresh!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal refresh data: {str(e)}")
    
    def open_hapus_rating(self):
        """Membuka window Hapus Rating"""
        self.hapus_rating_window = QtWidgets.QWidget()
        ui = Ui_WidgetHapusRating()
        ui.setupUi(self.hapus_rating_window)
        
        # TODO: Load data rating dari database
        # rating_data = db.get_all_ratings()
        # ui.load_rating_data(rating_data)
        
        self.hapus_rating_window.show()
    
    # ========== FUNGSI UNTUK TAB DATA USER ==========
    
    def refresh_users(self):
        """Refresh data user dari database"""
        try:
            # TODO: Query data user dari database
            # users = db.get_all_users()
            
            # Clear table
            self.ui.tableUsers.setRowCount(0)
            
            # TODO: Populate table dengan data dari database
            # for user in users:
            #     self.add_user_row(user)
            
            QMessageBox.information(self, "Refresh", "Data user berhasil di-refresh!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal refresh data: {str(e)}")
    
    # ========== FUNGSI UNTUK LOGOUT ==========
    
    def logout(self):
        """Logout dari aplikasi"""
        reply = QMessageBox.question(
            self, 
            'Konfirmasi Logout',
            'Apakah Anda yakin ingin keluar?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Clear session/token jika ada
            # session.clear()
            
            # Close window dan kembali ke login
            self.close()
            
            # TODO: Buka window login
            # login_window = LoginWindow()
            # login_window.show()
    
    # ========== FUNGSI HELPER ==========
    
    def load_all_data(self):
        """Load data awal untuk semua tab saat aplikasi dibuka"""
        try:
            # Load data untuk setiap tab
            self.refresh_bookings()
            self.refresh_payments()
            self.refresh_feedback()
            self.refresh_ratings()
            self.refresh_users()
        except Exception as e:
            print(f"Error loading initial data: {str(e)}")
    
    # ========== HELPER UNTUK POPULATE TABLE ==========
    
    def add_booking_row(self, booking):
        """Menambahkan baris data pemesanan ke table"""
        row = self.ui.tableBookings.rowCount()
        self.ui.tableBookings.insertRow(row)
        
        # TODO: Isi kolom-kolom dengan data booking
        # self.ui.tableBookings.setItem(row, 0, QtWidgets.QTableWidgetItem(booking['id']))
        # self.ui.tableBookings.setItem(row, 1, QtWidgets.QTableWidgetItem(booking['tanggal']))
        # ... dst
    
    def add_payment_row(self, payment):
        """Menambahkan baris data pembayaran ke table"""
        row = self.ui.tablePayments.rowCount()
        self.ui.tablePayments.insertRow(row)
        
        # TODO: Isi kolom-kolom dengan data payment
    
    def add_feedback_row(self, feedback):
        """Menambahkan baris data feedback ke table"""
        row = self.ui.tableFeedback.rowCount()
        self.ui.tableFeedback.insertRow(row)
        
        # TODO: Isi kolom-kolom dengan data feedback
    
    def add_rating_row(self, rating):
        """Menambahkan baris data rating ke table"""
        row = self.ui.tableRatings.rowCount()
        self.ui.tableRatings.insertRow(row)
        
        # TODO: Isi kolom-kolom dengan data rating
    
    def add_user_row(self, user):
        """Menambahkan baris data user ke table"""
        row = self.ui.tableUsers.rowCount()
        self.ui.tableUsers.insertRow(row)
        
        # TODO: Isi kolom-kolom dengan data user


def main():
    """Main function untuk menjalankan aplikasi"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set style aplikasi (opsional)
    app.setStyle('Fusion')
    
    # Create dan show main window
    window = AdminMainWindow()
    window.show()
    
    # Run aplikasi
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()