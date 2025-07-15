==============================
# ĐỒ ÁN 01: ỨNG DỤNG MÔ PHỎNG BẢO MẬT TÀI KHOẢN NGƯỜI DÙNG

File dữ liệu test được sử dụng trong [video demo](https://drive.google.com/drive/folders/1PuGn2AbgZ_b0iDku-1wlK-NTxLjEmHZU?usp=drive_link)

==============================

 MÔ TẢ
-----
1. Thư mục 'test image' bao gồm 2 ảnh:
- test.jpg: Ảnh có kích thước nhỏ (1.30MB)
- testOversize.png: Ảnh có kích thước lớn (6.20MB)
2. Thư mục 'encrypted':
- Ảnh 'test.jpg' được mã hóa theo định dạng "Gộp **.enc** và **khóa** vào **1 file**"
- Ảnh testOversize.png được mã hóa theo định dạng " Tách **.enc** + **.key**"
3. Trong file data 'users.json':
- Tài khoản 'admin@gmail.com' là **Quản trị viên (Admin)**
- Các tài khoản còn lại là **Người dùng thông thường (User)**
- Các tài khoản được đăng ký mặc định là **User**