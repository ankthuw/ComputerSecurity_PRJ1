import json
# import data
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from modules import file_encryptor, signature, session

class EncryptSignFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        tk.Button(self, text="Mã hóa tập tin", width=30, command=self.encrypt_file).pack(pady=5)
        tk.Button(self, text="Giải mã tập tin", width=30, command=self.decrypt_file).pack(pady=5)
        tk.Button(self, text="Ký số tập tin", width=30, command=self.sign_file).pack(pady=5)
        tk.Button(self, text="Xác minh chữ ký", width=30, command=self.verify_signature).pack(pady=5)

    def encrypt_file(self):
        sender = session.get_email()
        if not sender:
            messagebox.showerror("Lỗi", "Bạn cần đăng nhập để mã hóa tập tin.")
            return
        
        recipient = simpledialog.askstring("Người nhận", "Email người nhận:")
        if not recipient:
            return
        
        filepath = filedialog.askopenfilename(title="Chọn file cần mã hóa")
        if not filepath:
            return 
        
        merge = messagebox.askyesno("Lưu định dạng", "Gộp khóa vào file mã hóa?\n"
                                    "Yes -> 1 file .enc\n"
                                    "No -> 2 file: .enc và .key")
        ok, msg = file_encryptor.encrypt_file(sender, recipient, filepath, merge=merge)
        messagebox.showinfo("Mã hóa", msg)

    def decrypt_file(self):
        email = session.get_email()
        pw = session.get_passphrase()
        if not email or not pw:
            messagebox.showerror("Lỗi", "Bạn cần đăng nhập để giải mã tập tin.")
            return
        
        enc_path = filedialog.askopenfilename(title="Chọn file mã hóa (.enc)",
                                              filetypes=[("Encrypted Files", "*.enc"), ("All Files", "*.*")])
        if not enc_path:
            return
        
        try:
            with open(enc_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file mã hóa: {e}")
            return
        
        recipient = data["metadata"].get("recipient", "")
        if recipient and recipient != email:
            messagebox.showerror("Lỗi", "Bạn không phải là người nhận của file này.")
            return
        
        key_path = None
        if "encrypted_session_key" not in data:
            key_path = filedialog.askopenfilename(title="Chọn file khóa riêng tư (.key) - nếu có",
                                              filetypes=[("Private Key Files", "*.key"), ("All Files", "*.*")])
        
            if not key_path:
                messagebox.showwarning("Thiếu file khóa", "Không có khóa riêng tư để giải mã file.")
                return
            
        ok, msg = file_encryptor.decrypt_file(email, pw, enc_path, key_path=key_path)
        if ok:
            messagebox.showinfo("Giải mã", msg)
        else:
            messagebox.showerror("Giải mã thất bại", msg)
            return

    def sign_file(self):
        email = session.get_email()
        pwd = session.get_passphrase()
        if not email or not pwd:
            messagebox.showerror("Lỗi", "Bạn cần đăng nhập để ký số tập tin.")
            return
        
        file_path = filedialog.askopenfilename(title="Chọn file cần ký")
        if not file_path:
            return
        
        # from modules import signature
        ok, msg = signature.sign_file(file_path, email, pwd)
        messagebox.showinfo("Ký số", msg)

    def verify_signature(self):
        file_path = filedialog.askopenfilename(title="Chọn file gốc")
        sig_path = filedialog.askopenfilename(title="Chọn file chữ ký .sig")
        if not file_path or not sig_path:
            return
        
        # from modules import signature
        ok, msg = signature.verify_signature(file_path, sig_path)
        messagebox.showinfo("Xác minh chữ ký", msg)