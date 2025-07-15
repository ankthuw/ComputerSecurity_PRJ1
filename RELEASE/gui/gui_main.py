import tkinter as tk
from gui.gui_fit import center_window
from gui.gui_register_login import RegisterLoginFrame
from gui.gui_rsa_qr import RSAQRFrame
from gui.gui_encrypt_sign import EncryptSignFrame
from gui.gui_account_admin import AccountAdminFrame
from modules import session

class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Bảo mật")
        center_window(self)
        self.geometry("400x480")
        self.resizable(True, True)

        self.login_frame = None
        self.user_frame = None
        self.admin_frame = None
        
        self.login_label = None
        self.logout_button = None
        
        self.show_login()

    def show_login(self):
        if self.user_frame:
            self.user_frame.destroy()
            self.user_frame = None
        if self.admin_frame:
            self.admin_frame.destroy()
            self.admin_frame = None
        if self.login_frame:
            self.login_frame.destroy()
            self.login_frame = None

        self.login_frame = RegisterLoginFrame(self, on_login=self.show_dashboard)
        self.login_frame.pack(pady=20)

    def show_dashboard(self):

        if self.login_frame:
            self.login_frame.destroy()
            self.login_frame = None

        role = session.get_role()
        email = session.get_email()
        
        # Căn chỉnh kích thước cửa sổ
        self.geometry("400x800")
        center_window(self)

        self.login_label = tk.Label(self, text= f"Đang đăng nhập: {email} ({role})",
                         fg="green", font=("Arial", 10, "italic"))
        self.login_label.pack(pady=5)

        self.logout_button = tk.Button(self, text="Đăng xuất", command=self.logout)
        self.logout_button.pack(pady=10)
        
        self.user_frame = tk.Frame(self)
        self.user_frame.pack(pady=10)
        
        RSAQRFrame(self.user_frame)
        EncryptSignFrame(self.user_frame)
        AccountAdminFrame(self.user_frame)

    def logout(self):
        session.clear_session()
        
        if self.user_frame:
            self.user_frame.destroy()
            self.user_frame = None
            
        if self.admin_frame:
            self.admin_frame.destroy()
            self.admin_frame = None
            
        if self.login_label:
            self.login_label.destroy()
            self.login_label = None
            
        if self.logout_button:
            self.logout_button.destroy()
            self.logout_button = None
            
        self.show_login()

if __name__ == "__main__":
    app = MainGUI()
    app.mainloop()
