import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from modules import rsa_key_manager, qr_code_manager, session
from gui.utils import show_qr_with_text

class RSAQRFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        tk.Button(self, text="Tạo khóa RSA", width=30, command=self.create_key).pack(pady=5)
        tk.Button(self, text="Kiểm tra trạng thái khóa", width=30, command=self.check_key).pack(pady=5)
        tk.Button(self, text="Gia hạn khóa RSA", width=30, command=self.renew_key).pack(pady=5)
        tk.Button(self, text="Tạo mã QR từ public key", width=30, command=self.generate_qr).pack(pady=5)
        tk.Button(self, text="Đọc mã QR từ ảnh", width=30, command=self.read_qr).pack(pady=5)
        tk.Button(self, text="Tìm kiếm public key theo email", width=30, command=self.find_public_key).pack(pady=5)
        
    def get_user_session(self):
        email = session.get_email()
        pw = session.get_passphrase()
        if not email:
            messagebox.showwarning("Thông tin không đầy đủ", "Vui lòng đăng nhập trước khi thực hiện các thao tác.")
            return None, None
        return email, pw

    def create_key(self):
        email, pw = self.get_user_session()
        if email:
            ok, msg = rsa_key_manager.generate_rsa_keys(email, pw)
            messagebox.showinfo("Tạo khóa RSA", msg)

    def check_key(self):
        email, pw = self.get_user_session()
        if not email:
            messagebox.showwarning("Thông tin không đầy đủ", "Vui lòng đăng nhập trước khi kiểm tra khóa.")
            return
        msg = rsa_key_manager.check_key_status(email)
        messagebox.showinfo("Trạng thái khóa", msg)

    def renew_key(self):
        email, pw = self.get_user_session()
        if email:
            ok, msg = rsa_key_manager.renew_key(email)
            messagebox.showinfo("Gia hạn khóa", msg)

    def generate_qr(self):
        email, pw = self.get_user_session()
        ok, qr_path = qr_code_manager.create_qr_for_public_key(email)
        if not ok:
            messagebox.showerror("Mã QR", qr_path)
            return
        
        show_qr_with_text("Mã QR Public Key", f"Đã tạo mã QR cho email: {email} \nĐã lưu mã QR tại: {qr_path}", qr_path)
        
    def read_qr(self):
        path = filedialog.askopenfilename(title="Chọn ảnh QR")
        if path:
            ok, msg = qr_code_manager.read_qr_from_file(path)
            messagebox.showinfo("Quét mã QR", msg)

    def find_public_key(self):
        email = simpledialog.askstring("Email", "Nhập email cần tìm:")
        if email is None or not email.strip():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập email.")
            return
        
        ok, msg = qr_code_manager.find_public_key(email.strip())
        if not ok:
            messagebox.showinfor("Public Key", msg)
            return
        
        info_text, qr_path = msg
        show_qr_with_text("Public Key", info_text, qr_path)