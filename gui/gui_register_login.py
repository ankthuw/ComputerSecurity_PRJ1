import tkinter as tk
from tkinter import messagebox, ttk
from modules import register, login, session

class RegisterLoginFrame(tk.Frame):
    def __init__(self, master, on_login=None):
        super().__init__(master)
        self.on_login = on_login
        # self.pack()
        tk.Button(self, text="Đăng ký", width=25, command=self.register_view).pack(pady=5)
        tk.Button(self, text="Đăng nhập", width=25, command=self.login_view).pack(pady=5)
        tk.Button(self, text="Quên mật khẩu", width=25, command=self.recovery_view).pack(pady=5)
    def register_view(self):
        win = tk.Toplevel(self)
        win.title("Đăng ký tài khoản")

        fields = [
            ("Email", None),
            ("Họ tên", None),
            ("SĐT", None),
            ("Địa chỉ", None),
            ("Passphrase", "*")
        ]
        entries = {}

        for i, (label, mask) in enumerate(fields[:2]):
            tk.Label(win, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=4)
            entries[label] = tk.Entry(win, show=mask, width=30)
            entries[label].grid(row=i, column=1, columnspan=3, padx=5, pady=4)

        # Ngày sinh
        dob_row = 2
        tk.Label(win, text="Ngày sinh").grid(row=dob_row, column=0, sticky='w', padx=5, pady=6)
        tk.Label(win, text="Ngày").grid(row=dob_row, column=1, sticky='w')
        tk.Label(win, text="Tháng").grid(row=dob_row, column=2, sticky='w')
        tk.Label(win, text="Năm").grid(row=dob_row, column=3, sticky='w')

        day_cb = ttk.Combobox(win, values=[str(i).zfill(2) for i in range(1, 32)], width=5)
        month_cb = ttk.Combobox(win, values=[str(i).zfill(2) for i in range(1, 13)], width=5)
        year_cb = ttk.Combobox(win, values=[str(i) for i in range(1950, 2026)], width=7)

        day_cb.grid(row=dob_row + 1, column=1, padx=5, pady=2)
        month_cb.grid(row=dob_row + 1, column=2, padx=5, pady=2)
        year_cb.grid(row=dob_row + 1, column=3, padx=5, pady=2)

        # Các trường còn lại: SĐT, Địa chỉ, Passphrase
        for j, (label, mask) in enumerate(fields[2:], start=dob_row + 2):
            tk.Label(win, text=label).grid(row=j, column=0, sticky='w', padx=5, pady=4)
            entries[label] = tk.Entry(win, show=mask, width=30)
            entries[label].grid(row=j, column=1, columnspan=3, padx=5, pady=4)

        def submit():
            if not all(entries[field].get().strip() for field in ["Email", "Họ tên", "SĐT", "Địa chỉ", "Passphrase"]):
                messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường.")
                return
            if not (day_cb.get() and month_cb.get() and year_cb.get()):
                messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn ngày sinh đầy đủ.")
                return
            
            dob = f"{year_cb.get()}-{month_cb.get()}-{day_cb.get()}"
            ok, msg = register.register_user(
                entries["Email"].get(), entries["Họ tên"].get(), dob,
                entries["SĐT"].get(), entries["Địa chỉ"].get(), entries["Passphrase"].get()
            )
            if ok:
                recovery_key = msg
                
                def copy_recovery_key():
                    win.clipboard_clear()
                    win.clipboard_append(recovery_key)
                    messagebox.showinfo("Đã copy", "Recovery Key đã được sao chép vào clipboard.")
                    
                popup = tk.Toplevel(win)
                popup.title("Recovery Key")
                popup.geometry("420x210")
                popup.resizable(False, False)

                tk.Label(popup, text="Mã khôi phục của bạn (chỉ hiển thị 1 lần)", fg="blue", font=("Arial", 11, "bold")).pack(pady=(10, 5))

                entry = tk.Entry(popup, width=45, justify="center", font=("Courier", 10))
                entry.insert(0, recovery_key)
                entry.config(state="readonly")
                entry.pack(pady=5)
                
                tk.Label(
                    popup,
                    text="Vui lòng lưu mã này ở nơi an toàn. Nếu mất, bạn sẽ KHÔNG thể khôi phục tài khoản.",
                    fg="red", wraplength=380, justify="center", font=("Arial", 9, "italic")
                ).pack(pady=5)

                tk.Button(popup, text="Sao chép mã", command=copy_recovery_key).pack(pady=(5, 3))
                tk.Button(popup, text="Đóng", command=popup.destroy).pack(pady=(0, 10))

        tk.Button(win, text="Đăng ký", width=20, command=submit).grid(row=j+1, column=0, columnspan=4, pady=10)

    def login_view(self):
        win = tk.Toplevel(self)
        win.title("Đăng nhập")
        tk.Label(win, text="Email").grid(row=0, column=0)
        email = tk.Entry(win)
        email.grid(row=0, column=1)
        tk.Label(win, text="Passphrase").grid(row=1, column=0)
        password = tk.Entry(win, show="*")
        password.grid(row=1, column=1)

        def submit():
            ok, msg, role = login.login(email.get(), password.get())
            if ok:
                otp = tk.simpledialog.askstring("TOTP", "Nhập mã xác thực từ Google Authenticator:")
                if otp is None:
                    messagebox.showinfo("Hủy xác thực", "Bạn đã hủy xác thực TOTP.")
                    return
                ok2, msg2 = login.verify_totp(email.get(), otp)
                if ok2:
                    session.set_user(email.get(), password.get(), role)
                    messagebox.showinfo("Thông báo", msg2)
                    if self.on_login:
                        self.on_login()
                    win.destroy()
                else:
                    messagebox.showwarning("Lỗi", msg2)
            else:
                messagebox.showwarning("Lỗi", msg)

        tk.Button(win, text="Đăng nhập", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
        
    def recovery_view(self):
        win = tk.Toplevel(self)
        win.title("Khôi phục tài khoản")

        tk.Label(win, text="Email").grid(row=0, column=0)
        email_entry = tk.Entry(win, width=30)
        email_entry.grid(row=0, column=1)

        tk.Label(win, text="Recovery Key").grid(row=1, column=0)
        key_entry = tk.Entry(win, width=30)
        key_entry.grid(row=1, column=1)

        tk.Label(win, text="Passphrase mới").grid(row=2, column=0)
        new_entry = tk.Entry(win, width=30, show="*")
        new_entry.grid(row=2, column=1)

        def submit():
            email = email_entry.get().strip()
            key = key_entry.get().strip()
            new_pass = new_entry.get().strip()

            if not all([email, key, new_pass]):
                messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đủ các trường.")
                return
            
            from modules import account_manager
            ok, msg = account_manager.recover_account(email, key, new_pass)
            if ok:
                messagebox.showinfo("Thành công", msg)
                win.destroy()
            else:
                messagebox.showerror("Thất bại", msg)

        tk.Button(win, text="Khôi phục", command=submit).grid(row=3, column=0, columnspan=2, pady=10)