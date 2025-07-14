import os
from PIL import Image, ImageTk
import tkinter as tk

def show_qr_popup(qr_path, title, message):
    """Hiển thị mã QR trong một popup."""
    popup = tk.Toplevel()
    popup.title(title)
    
    label = tk.Label(popup, text=message)
    label.pack(pady=10)

    # Load và hiển thị ảnh mã QR
    img = Image.open(qr_path)
    img = img.resize((200, 200))
    photo = ImageTk.PhotoImage(img)

    img_label = tk.Label(popup, image=photo)
    img_label.image = photo  # Keep a reference to avoid garbage collection
    img_label.pack(pady=10)

    tk.Button(popup, text="Đóng", command=popup.destroy).pack(pady=10)

    popup.grab_set() 
    popup.wait_window()
    
    
def show_qr_with_text(title_text, info_text, qr_path=None):
    win = tk.Toplevel()
    win.title(title_text)
    
    # Hiển thị thông tin văn bản
    text = tk.Text(win, height=15, width=80, wrap="word")
    text.insert("1.0", info_text)
    text.config(state="disabled")
    text.pack(padx=10, pady=10)

    # Hiển thị ảnh QR nếu có
    if qr_path and os.path.exists(qr_path):
        img = Image.open(qr_path).resize((200, 200))
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(win, image=photo)
        img_label.image = photo
        img_label.pack(pady=(0, 10))

    tk.Button(win, text="Đóng", command=win.destroy).pack(pady=5)