import tkinter as tk
from tkinter import simpledialog, messagebox
from modules import account_manager, admin_tools, session
from modules import login

class AccountAdminFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # self.pack()
        role = session.get_role()
        show_any = False
        
        if role in ("user", "admin"):
            # for all users
            tk.Button(self, text="Cập nhật thông tin cá nhân", width=35, command=self.update_info).pack(pady=3)
            tk.Button(self, text="Đổi passphrase", width=35, command=self.change_pass).pack(pady=3)
            # tk.Button(self, text="Khôi phục tài khoản", width=35, command=self.recover_account).pack(pady=3)
            show_any = True
            
        if role == "admin":
            # for admin only
            tk.Button(self, text="Xem danh sách người dùng", width=35, command=self.view_users).pack(pady=3)
            tk.Button(self, text="Khóa/Mở khóa tài khoản người dùng", width=35, command=self.toggle_user).pack(pady=3)
            tk.Button(self, text="Xem log hệ thống", width=35, command=self.view_logs).pack(pady=3)
            show_any = True
            
        if show_any:
            self.pack()

    def update_info(self):
        email = session.get_email()
        
        dialog = tk.Toplevel(self)
        dialog.title("Cập nhật thông tin cá nhân")
        dialog.transient(self)
        dialog.grab_set()
        
        entries = {}
        fields = ["Họ tên", "Ngày sinh (YYYY-MM-DD)", "Số điện thoại", "Địa chỉ"]
        for i, label in enumerate(fields):
            tk.Label(dialog, text=label+ ":").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry
            
        def submit():
            name = entries["Họ tên"].get().strip()
            dob = entries["Ngày sinh (YYYY-MM-DD)"].get().strip()
            phone = entries["Số điện thoại"].get().strip()
            address = entries["Địa chỉ"].get().strip()
            
            ok, msg = account_manager.update_profile(email, name, dob, phone, address)
            messagebox.showinfo("Cập nhật thông tin", msg)
            dialog.destroy()
            
        tk.Button(dialog, text="Xác nhận", command=submit).grid(row=len(fields), column=0, columnspan=2, pady=10)
        dialog.wait_window()

    def change_pass(self):
        email = session.get_email()
        
        dialog = tk.Toplevel(self)
        dialog.title("Đổi Passphrase")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Passphrase cũ:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        old_entry = tk.Entry(dialog, show="*", width=30)
        old_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Passphrase mới:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        new_entry = tk.Entry(dialog, show="*", width=30)
        new_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def submit():
            old_pass = old_entry.get().strip()
            new_pass = new_entry.get().strip()
            
            if not old_pass or not new_pass:
                messagebox.showwarning("Thông tin không đầy đủ", "Vui lòng điền đầy đủ thông tin.")
                return
            ok, msg = account_manager.change_passphrase(email, old_pass, new_pass)
            messagebox.showinfo("Đổi Passphrase", msg)
            dialog.destroy()
            
        tk.Button(dialog, text="Xác nhận", command=submit).grid(row=2, column=0, columnspan=2, pady=10)
        dialog.wait_window()

    def recover_account(self):
        dialog = tk.Toplevel(self)
        dialog.title("Khôi phục tài khoản")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        email_entry = tk.Entry(dialog, width=30)
        email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Recovery Key:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        recovery_entry = tk.Entry(dialog, width=30)
        recovery_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Passphrase mới:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        new_pass_entry = tk.Entry(dialog, show="*", width=30)
        new_pass_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def submit():
            email = email_entry.get().strip()
            recovery_key = recovery_entry.get().strip()
            new_pass = new_pass_entry.get().strip()
            
            if not email or not recovery_key or not new_pass:
                messagebox.showwarning("Thông tin không đầy đủ", "Vui lòng điền đầy đủ thông tin.")
                return
            
            ok, msg = account_manager.recover_account(email, recovery_key, new_pass)
            messagebox.showinfo("Khôi phục tài khoản", msg)
            dialog.destroy()
            
        tk.Button(dialog, text="Xác nhận", command=submit).grid(row=3, column=0, columnspan=2, pady=10)
        dialog.wait_window()
        
    def view_users(self):
        email = session.get_email()
        ok, msg = admin_tools.view_all_users(email)
        messagebox.showinfo("Danh sách người dùng", msg)
        
    def toggle_user(self):
        dialog = tk.Toplevel(self)
        dialog.title("Khóa/Mở khóa tài khoản")
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Email người dùng:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        email_entry = tk.Entry(dialog, width=30)
        email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Hành động:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        action_var = tk.StringVar(value="lock")
        frame_actions = tk.Frame(dialog)
        frame_actions.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        tk.Radiobutton(frame_actions, text="Khóa", variable=action_var, value="lock").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_actions, text="Mở khóa", variable=action_var, value
                        ="unlock").pack(side=tk.LEFT, padx=5)
        
        def submit():
            email = email_entry.get().strip()
            action = action_var.get()
            
            if not email:
                messagebox.showwarning("Thông tin không đầy đủ", "Vui lòng nhập email người dùng.")
                return
            
            ok, msg = admin_tools.toggle_user_account(email, action)
            messagebox.showinfo("Khóa/Mở khóa tài khoản", msg)
            dialog.destroy()
            
        tk.Button(dialog, text="Xác nhận", command=submit).grid(row=2, column=0, columnspan=3, pady=10)
        dialog.wait_window()
        
    def view_logs(self):
        email = session.get_email()
        ok, logs = admin_tools.view_system_logs(email)
        if not ok:
            messagebox.showerror("Lỗi", logs)
            return
        
        log_window = tk.Toplevel(self)
        log_window.title("Log hệ thống")
        log_window.transient(self)
        log_window.grab_set()
        
        text = tk.Text(log_window, wrap=tk.WORD, width=80, height=20)
        text.insert(tk.END, logs)
        text.config(state=tk.DISABLED)  
        text.pack(padx=10, pady=10)
        tk.Button(log_window, text="Đóng", command=log_window.destroy).pack(pady=5)
        log_window.wait_window()
        