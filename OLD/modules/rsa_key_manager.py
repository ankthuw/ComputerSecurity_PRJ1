# Chức năng 3, 13: Tạo/kiểm tra/gia hạn khóa RSA (mã hóa bằng AES từ passphrase)
import json, os
import base64
from datetime import datetime, timedelta
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from modules.logger import write_log

USER_FILE = "data/users.json"
RSA_DIR = "data/keys/"
os.makedirs(RSA_DIR, exist_ok=True)

# Hàm tạo khóa RSA và lưu
def generate_rsa_keys(email, passphrase):
    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if email not in users:
        return False, "Không tìm thấy người dùng."

    # Sinh cặp khóa RSA
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    created_at = datetime.now().isoformat()
    expire_at = (datetime.now() + timedelta(days=90)).isoformat()

    # Dùng passphrase tạo AES key để mã hóa private key
    salt = get_random_bytes(16)
    aes_key = PBKDF2(passphrase, salt, dkLen=32)
    cipher = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(private_key)

    encrypted_data = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

    users[email]["rsa_keys"] = {
        "public_key": base64.b64encode(public_key).decode(),
        "private_key_encrypted": encrypted_data,
        "created_at": created_at,
        "expire_at": expire_at
    }

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

    with open(f"{RSA_DIR}/public_{email}.pem", "wb") as f:
        f.write(public_key)

    write_log(email, "RSA", "Tạo khóa RSA thành công")
    return True, "Tạo khóa RSA thành công."

# Kiểm tra trạng thái khóa
def check_key_status(email):
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except Exception:
        return "Lỗi khi đọc file người dùng."

    if email not in users or not users[email].get("rsa_keys"):
        write_log(email, "RSA", "Kiểm tra trạng thái khóa: Không có khóa")
        return "Không có khóa RSA."

    rsa = users[email]["rsa_keys"]

    try:
        created_at = datetime.fromisoformat(rsa["created_at"])
        expire_at = datetime.fromisoformat(rsa["expire_at"])
    except Exception:
        write_log(email, "RSA", "Lỗi định dạng ngày tạo/hết hạn")
        return "Lỗi: Không đọc được ngày tạo hoặc hạn dùng của khóa."

    now = datetime.now()
    days_left = (expire_at - now).days
    
    if expire_at < now:
        status = "Hết hạn"
        days_text = f"Hết hạn {abs(days_left)} ngày trước"
    elif (expire_at - now).days <= 7:
        status = "Gần hết hạn"
        days_text = f"Còn {days_left} ngày"
    else:
        status = "Còn hạn"
        days_text = f"Còn {days_left} ngày" if days_left > 0 else "Hết hạn ngay hôm nay"

    write_log(email, "RSA", f"Kiểm tra trạng thái khóa: {status}")

    return (
        f"Trạng thái khóa: {status} ({days_text})\n"
        f"Ngày tạo: {created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Hết hạn: {expire_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

# Gia hạn khóa RSA (thêm 90 ngày nữa), xác thực passphrase
def renew_key(email):
    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if email not in users or not users[email].get("rsa_keys"):
        return False, "Không có khóa để gia hạn."

    enc_data = users[email]["rsa_keys"]["private_key_encrypted"]
    try:
        salt = base64.b64decode(enc_data["salt"])
        nonce = base64.b64decode(enc_data["nonce"])
        tag = base64.b64decode(enc_data["tag"])
        ciphertext = base64.b64decode(enc_data["ciphertext"])
        
        aes_key = PBKDF2(users[email]["passphrase"], salt, dkLen=32)
        cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
        _ = cipher.decrypt_and_verify(ciphertext, tag)
    except Exception as e:
        write_log(email, "RSA", "Gia hạn thất bại - Sai passphrase")
        return False, "Lỗi khi giải mã khóa. Vui lòng kiểm tra passphrase."
    
    expire_new = datetime.now() + timedelta(days=90)
    users[email]["rsa_keys"]["expire_at"] = expire_new.isoformat()

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

    write_log(email, "RSA", "Gia hạn khóa thành công")
    return True, "Gia hạn thành công."
