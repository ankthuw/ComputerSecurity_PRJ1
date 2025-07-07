# Chức năng 5, 17: Cập nhật tài khoản, đổi passphrase, khôi phục tài khoản
import json, os, base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from modules.logger import write_log

USER_FILE = "data/users.json"

# Hàm hash passphrase
def hash_passphrase(passphrase, salt):
    return hashlib.sha256(salt + passphrase.encode()).hexdigest()

# Giải mã private key AES
def decrypt_private_key(enc_data, passphrase):
    try:
        salt = base64.b64decode(enc_data["salt"])
        nonce = base64.b64decode(enc_data["nonce"])
        tag = base64.b64decode(enc_data["tag"])
        ciphertext = base64.b64decode(enc_data["ciphertext"])
        aes_key = PBKDF2(passphrase, salt, dkLen=32)
        cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
        private_key = cipher.decrypt_and_verify(ciphertext, tag)
        return True, private_key
    except Exception as e:
        return False, str(e)

# Mã hóa lại private key
def reencrypt_private_key(private_key, new_passphrase):
    salt = os.urandom(16)
    aes_key = PBKDF2(new_passphrase, salt, dkLen=32)
    cipher = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(private_key)
    return {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(cipher.nonce).decode(),
        "tag": base64.b64encode(tag).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

# Đổi passphrase sau khi đăng nhập
def change_passphrase(email, old_pass, new_pass):
    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if email not in users:
        return False, "Email không tồn tại."

    user = users[email]
    salt = base64.b64decode(user["salt"])
    if hash_passphrase(old_pass, salt) != user["pass_hash"]:
        return False, "Sai passphrase cũ."

    if user.get("rsa_keys"):
        ok, priv = decrypt_private_key(user["rsa_keys"]["private_key_encrypted"], old_pass)
        if not ok:
            return False, "Không giải mã được private key cũ."

        new_encrypted = reencrypt_private_key(priv, new_pass)
        user["rsa_keys"]["private_key_encrypted"] = new_encrypted

    new_salt = os.urandom(16)
    user["salt"] = base64.b64encode(new_salt).decode()
    user["pass_hash"] = hash_passphrase(new_pass, new_salt)

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

    write_log(email, "ChangePass", "Success")
    return True, "Đã đổi passphrase thành công."

# Sửa thông tin cơ bản
def update_profile(email, name=None, dob=None, phone=None, address=None):
    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if email not in users:
        return False, "Không tìm thấy người dùng."

    user = users[email]
    if name: user["name"] = name
    if dob:
        try:
            # kiểm tra định dạng ngày tháng
            from datetime import datetime
            datetime.strptime(dob, "%Y-%m-%d")
            user["dob"] = dob
        except ValueError:
            # write_log(email, "UpdateInfo", "InvalidDOB")
            return False, "Định dạng ngày sinh không hợp lệ. Vui lòng sử dụng YYYY-MM-DD."
    if phone:
        if not phone.isdigit():
            return False, "Số điện thoại không hợp lệ. Chỉ chứa chữ số."
        user["phone"] = phone
    if address: user["address"] = address

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

    write_log(email, "UpdateInfo", "Success")
    return True, "Đã cập nhật thông tin cá nhân."

# Khôi phục tài khoản bằng recovery key
def recover_account(email, recovery_key, new_passphrase):
    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if email not in users:
        return False, "Không tìm thấy người dùng."

    user = users[email]
    if user.get("recovery_key") != recovery_key:
        return False, "Mã khôi phục không hợp lệ."

    # Nếu có RSA thì giải mã → mã hóa lại
    if user.get("rsa_keys"):
        enc = user["rsa_keys"]["private_key_encrypted"]
        old_pass = user["pass_hash"]
        ok, priv = decrypt_private_key(enc, old_pass)
        if not ok:
            return False, "Không thể giải mã private key bằng pass cũ."

        new_enc = reencrypt_private_key(priv, new_passphrase)
        user["rsa_keys"]["private_key_encrypted"] = new_enc

    new_salt = os.urandom(16)
    user["salt"] = base64.b64encode(new_salt).decode()
    user["pass_hash"] = hash_passphrase(new_passphrase, new_salt)

    # Vô hiệu hóa recovery key sau 1 lần dùng
    # user["recovery_key"] = None

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

    write_log(email, "RecoverAccount", "Success")
    return True, "Khôi phục tài khoản thành công. Hãy lưu lại passphrase mới."
