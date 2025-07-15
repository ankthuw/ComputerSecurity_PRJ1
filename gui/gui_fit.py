# Căn chỉnh cửa sổ hiển thị ở giữa màn hình

def center_window(window):
    # Sửa đổi kích thước cửa sổ để nó có thể hiển thị đúng

    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

