==============================
# ĐỒ ÁN 01: ỨNG DỤNG MÔ PHỎNG BẢO MẬT TÀI KHOẢN NGƯỜI DÙNG

==============================

MÔ TẢ
-----
Ứng dụng được xây dựng nhằm mô phỏng một hệ thống bảo mật tài khoản người dùng với đầy đủ các chức năng như:
- Đăng ký / Đăng nhập an toàn
- Xác thực đa yếu tố TOTP (2FA)
- Mã hóa và giải mã tập tin bằng RSA + AES (AES-GCM)
- Ký số và xác minh chữ ký tập tin
- Phân quyền Admin / User
- Ghi log bảo mật và sự kiện
- Chia nhỏ và khôi phục file lớn
- Khôi phục tài khoản bằng mã khôi phục
- Giao diện GUI trực quan, thân thiện với người dùng


CÀI ĐẶT & CHẠY CHƯƠNG TRÌNH
---------------------------
1. Cài đặt thư viện:
   > pip install -r requirements.txt

2. Chạy chương trình:
   > python main.py


HƯỚNG DẪN SỬ DỤNG
-----------------
Sau khi chạy chương trình, giao diện chính sẽ xuất hiện với các chức năng chính:

1. **Đăng ký tài khoản:**
   - Nhập đầy đủ thông tin yêu cầu như email, passphrase và xác nhận passphrase...
   * Lưu ý rằng passphrase phải có ít nhất 8 ký tự, bao gồm chữ hoa, số và ký tự đặc biệt.
   - Ứng dụng sẽ tạo cặp khóa RSA và mã hóa khóa riêng bằng AES-EAX.
   - Khi đăng nhập thành công lần đầu, hệ thống sẽ cung cấp Recovery Key để lưu lại và sử dụng khi quên passphrase.

2. **Đăng nhập và xác thực TOTP:**
   - Sau khi nhập đúng thông tin đăng nhập, người dùng sẽ được yêu cầu nhập mã TOTP từ ứng dụng Google Authenticator.
   - Sau 5 lần nhập sai liên tiếp, tài khoản bị tạm khóa trong 5 phút.

3. **Quản lý khóa RSA:**
   - Tạo khóa RSA mới.
   - Xem trạng thái khóa, ngày tạo và cho phép gia hạn nếu cần.


4. **QR code:**
   - Tạo QR code chứa thông tin public key.
   - Quét hình ảnh chứa QR code và lưu thông tin public key.

3. **Mã hóa tập tin:**
   - Chọn file cần mã hóa.
   - Hệ thống sử dụng AES-GCM để mã hóa nội dung và RSA-OAEP để mã hóa khóa AES.
   - File kết quả gồm `.enc` và `.key`, có thể lưu gộp hoặc tách.

4. **Giải mã tập tin:**
   - Chọn file `.enc` và file khóa `.key`.
   - Nhập đúng passphrase để giải mã thành công.

5. **Ký số tập tin:**
   - Chọn file cần ký, hệ thống sử dụng khóa riêng (private key) để tạo chữ ký số.
   - File `.sig` sẽ được sinh ra kèm theo.

6. **Xác minh chữ ký số:**
   - Cung cấp file gốc, file chữ ký `.sig` và khóa công khai.
   - Hệ thống sẽ kiểm tra tính hợp lệ và hiển thị kết quả.

8. **Quản lý tài khoản cá nhân:**
   - Cập nhật thông tin cá nhân, đổi passphrase, khôi phục tài khoản bằng Recovery Key nếu quên pass.

9. **Chức năng nâng cao của Admin:**
   - Xem danh sách người dùng, khóa / mở tài khoản, xem log hệ thống.

10. **Ghi log bảo mật:**
    - Tự động ghi lại mọi hành động quan trọng vào `security.log` để giám sát và truy vết.

LIÊN KẾT
---------
[Link Video demo (Google Drive)](https://drive.google.com/drive/folders/1PuGn2AbgZ_b0iDku-1wlK-NTxLjEmHZU?usp=drive_link)

PHỤ TRÁCH & TÁC GIẢ
--------------------
- Sinh viên thực hiện: 
    - Bế Lã Anh Thư - 22127402
    - Võ Hữu Tuấn - 22127439
- Giảng viên hướng dẫn:
    - Thầy Phan Quốc Kỳ
    - Thầy Lê Hà Minh
    - Thầy Lê Giang Thanh

- Lớp học phần: An ninh máy tính - 22MMT
