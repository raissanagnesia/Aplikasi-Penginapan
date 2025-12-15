import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer

from tampilan_awal import Ui_WelcomeForm
from login import Ui_LoginForm
from dashboard_user_ui import Ui_DashboardAdmin


# =========================
#   TAMPILAN AWAL (WELCOME)
# =========================
class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_WelcomeForm()
        self.ui.setupUi(self)

        # tombol login → pindah ke login
        self.ui.btnLogin.clicked.connect(self.goToLogin)

    def goToLogin(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()


# =========================
#           LOGIN
# =========================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)

        # tombol login → dashboard
        self.ui.btnLogin.clicked.connect(self.goToDashboard)

    def goToDashboard(self):
        self.dashboard = DashboardWindow()
        self.dashboard.show()
        self.close()


# =========================
#        DASHBOARD USER
# =========================
class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DashboardAdmin()
        self.ui.setupUi(self)


# =========================
#        MAIN APP
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    welcome = WelcomeScreen()
    welcome.show()

    sys.exit(app.exec())