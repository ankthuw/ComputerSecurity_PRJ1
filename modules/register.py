import json, os, hashlib, base64, re
from datetime import datetime

USER_FILE = "data/users.json"
LOG_FILE = "data/security.log"

# Tạo salt ngẫu nhiên
def generate_salt():
    return os.urandom(16)

# Băm passphrase với salt
def hash_passphrase(passphrase, salt):
    return hashlib.sha256(salt + passphrase.encode()).hexdigest()

# Ghi log hành động
def write_log(email, action, status):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {email} | {action} | {status}\n")

# Hàm đăng ký
def register_user(email, name, dob, phone, address, passphrase):
    users = {}

    # Đọc dữ liệu nếu file tồn tại và hợp lệ
    if os.path.exists(USER_FILE) and os.path.getsize(USER_FILE) > 0:
        try:
            with open(USER_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = {}  # fallback nếu file bị hỏng

    if email in users:
        write_log(email, "Register", "Failed - Email exists")
        return False, "Email đã tồn tại!"
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Email không hợp lệ!"
    
    if len(passphrase) < 8 or not any(c.isupper() for c in passphrase) \
        or not any(c.isdigit() for c in passphrase) \
        or not any(not c.isalnum() for c in passphrase):
        write_log(email, "Register", "Failed - Weak passphrase")
        return False, "Passphrase yếu! Cần ít nhất 8 ký tự, bao gồm chữ hoa, số và ký tự đặc biệt."

    try:
        dob_obj = datetime.strptime(dob, "%Y-%m-%d")
        if dob_obj > datetime.now():
            return False, "Ngày sinh không hợp lệ!"
    except ValueError:
        return False, "Ngày sinh không hợp lệ! Định dạng: YYYY-MM-DD"
    
    if not phone.isdigit():
        return False, "Số điện thoại không hợp lệ! Chỉ chứa chữ số."
    
    if not name.strip() or not address.strip():
        return False, "Tên và địa chỉ không được để trống!"
    
    salt = generate_salt()
    hashed = hash_passphrase(passphrase, salt)
    recovery_key = base64.urlsafe_b64encode(os.urandom(12)).decode()

    users[email] = {
        "name": name,
        "dob": dob,
        "phone": phone,
        "address": address,
        "salt": base64.b64encode(salt).decode(),
        "pass_hash": hashed,
        "role": "user",
        "is_locked": False,
        "login_attempts": 0,
        "recovery_key": recovery_key,
        "rsa_keys": None
    }

    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

    write_log(email, "Register", "Success")
    return True, recovery_key
