# Chức năng 2: Đăng nhập & Xác thực đa yếu tố (TOTP/OTP, giới hạn đăng nhập)
import json, os, time
import hashlib, base64
import pyotp
import qrcode
from datetime import datetime, timedelta
from modules.logger import write_log
from modules.session import current_user

USER_FILE = "data/users.json"

# Hàm hash lại passphrase với salt
def hash_passphrase(passphrase, salt):
    return hashlib.sha256(salt + passphrase.encode()).hexdigest()

# Kiểm tra đăng nhập và sinh QR nếu chưa có secret
def login(email, passphrase):
    if not os.path.exists(USER_FILE):
        return False, "Chưa có người dùng nào đăng ký.", None

    with open(USER_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    if email not in users:
        write_log(email, "Login", "Failed - Email không tồn tại")
        return False, "Email không tồn tại.", None

    user = users[email]

    # Kiểm tra người dùng có bị khóa hay không
    if user.get("is_locked"):
        write_log(email, "Login", "Blocked - Tài khoản bị khóa bởi admin")
        return False, "Tài khoản bị khóa bởi admin. Vui lòng liên hệ quản trị viên.", None
    
    if user.get("temp_lock_time"):
        elapsed = time.time() - user["temp_lock_time"]
        if elapsed < 300:
            remaining = int(300 - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60
            write_log(email, "Login", f"Blocked - Khóa tạm thời {seconds} giây")
            return False, f"Tài khoản bị khóa tạm thời. Vui lòng thử lại sau {minutes} phút {seconds} giây.", None
        else:
            user.pop("temp_lock_time", None) 
            user["login_attempts"] = 0

    salt = base64.b64decode(user["salt"])
    hashed_input = hash_passphrase(passphrase, salt)

    if hashed_input != user["pass_hash"]:
        user["login_attempts"] = user.get("login_attempts", 0) + 1
        attempts = user["login_attempts"]
        
        if attempts >= 5:
            user["temp_lock_time"] = time.time()  
            write_log(email, "Login", f"Failed - Sai passphrase lần {attempts}, bị tạm khóa")
            msg = "Tài khoản bị khóa tạm thời 5 phút do nhập sai quá nhiều lần."
        else:
            write_log(email, "Login", f"Failed - Sai passphrase lần {attempts}")
            msg = f"Sai passphrase. Bạn còn {5 - attempts} lần thử nữa."
            
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return False, msg, None
    
    # Dăng nhập thành công
    user["login_attempts"] = 0  # Reset attempts on successful login
    user.pop("temp_lock_time", None)

    # Nếu chưa có secret TOTP thì tạo
    if "totp_secret" not in user:
        user["totp_secret"] = pyotp.random_base32()
        totp_uri = pyotp.totp.TOTP(user["totp_secret"]).provisioning_uri(
            name=email, issuer_name="SecApp"
        )
        qr = qrcode.make(totp_uri)
        qr_path = f"data/qrcodes/totp_{email.replace('@', '_')}.png"
        qr.save(qr_path)
        
        from gui.utils import show_qr_popup
        show_qr_popup(qr_path, "TOTP QR Code", "Quét mã QR để thiết lập TOTP.")
        
        msg = "Quét mã QR để kích hoạt TOTP (Google Authenticator)."
    else:
        msg = "Nhập mã TOTP từ ứng dụng Google Authenticator."

    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

    write_log(email, "Login", "Success - Đã xác minh passphrase")
    return True, msg, user["role"]

# Xác minh mã TOTP từ người dùng
def verify_totp(email, otp_input):
    with open(USER_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    if email not in users:
        return False, "Email không tồn tại."

    user = users[email]
    if "totp_secret" not in user:
        return False, "Chưa thiết lập TOTP."

    totp = pyotp.TOTP(user["totp_secret"])
    if totp.verify(otp_input):
        write_log(email, "MFA", "Success")
        
        current_user["email"] = email
        current_user["passphrase"] = user["pass_hash"]
        
        return True, "Xác thực thành công."
    else:
        write_log(email, "MFA", "Failed - Sai mã TOTP")
        return False, "Sai mã xác thực."

# Lấy vai trò của người dùng từ file users.json
def get_user_role(email):
    with open("data/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    return users[email].get("role", "user")
