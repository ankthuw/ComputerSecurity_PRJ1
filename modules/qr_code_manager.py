# Chức năng 4, 14: Tạo & đọc QR chứa public key, tìm kiếm theo email
import json, os, base64
import qrcode
from datetime import datetime
from pyzbar.pyzbar import decode
from PIL import Image,ImageTk
from modules.logger import write_log

USER_FILE = "data/users.json"
QR_DIR = "data/qrcodes/"
os.makedirs(QR_DIR, exist_ok=True)

# Tạo QR code chứa public key + metadata
def create_qr_for_public_key(email):
    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if email not in users or not users[email].get("rsa_keys"):
        return False, "Không tìm thấy public key."

    pubkey = users[email]["rsa_keys"]["public_key"]
    created_at = users[email]["rsa_keys"]["created_at"]

    qr_data = {
        "email": email,
        "created_at": created_at,
        "public_key": pubkey
    }

    img = qrcode.make(json.dumps(qr_data))
    path = f"{QR_DIR}/qr_{email.replace('@', '_')}.png"
    img.save(path)

    write_log(email, "QR", "Tạo QR code thành công")
    return True, path

# Đọc QR code từ file và lưu vào danh sách public key
def read_qr_from_file(file_path):
    if not os.path.exists(file_path):
        return False, "Không tìm thấy file QR."

    img = Image.open(file_path)
    data = decode(img)
    if not data:
        return False, "Không quét được mã QR."

    try:
        raw = data[0].data.decode()   
        qr_content = json.loads(raw)
    except Exception as e:
        return False, f"Nội dung mã QR không hợp lệ!"

    # Lưu public key vào danh sách public keys
    if not os.path.exists("data/public_keys.json"):
        with open("data/public_keys.json", "w") as f:
            json.dump({}, f, indent=2)
            
    with open("data/public_keys.json", "r+") as f:
        try:
            pkdb = json.load(f)
        except:
            pkdb = {}

        pkdb[qr_content["email"]] = {
            "created_at": qr_content["created_at"],
            "public_key": qr_content["public_key"]
        }
        f.seek(0)
        json.dump(pkdb, f, indent=2)
        
    result = f"""Public Key đã quét:
    Email: {qr_content['email']}
    Ngày tạo: {qr_content['created_at']}
    Public Key: {qr_content['public_key'][:100]}...
    
    Đã lưu vào data/public_keys.json
    """

    return True, result

def find_public_key(email):
    safe_email = email.replace("@", "_")
    pem_path = f"data/keys/public_{safe_email}.pem"
    qr_path = f"data/qrcodes/qr_{safe_email}.png"
    users_file = "data/users.json"

    if not os.path.exists(users_file):
        return False, "Không tìm thấy dữ liệu người dùng."

    with open(users_file, "r", encoding="utf-8") as f:
        users = json.load(f)

    if email not in users or "rsa_keys" not in users[email]:
        return False, "Không tìm thấy public key cho email này."

    rsa = users[email]["rsa_keys"]
    public_key_b64 = rsa.get("public_key", "")[:100] + "..."
    created_at = rsa.get("created_at", "Không rõ")
    expire_at = rsa.get("expire_at", "")

    if expire_at:
        days_left = (datetime.fromisoformat(expire_at) - datetime.now()).days
        status = f"{days_left} ngày còn lại" if days_left >= 0 else "Đã hết hạn"
    else:
        status = "Không rõ"

    has_qr = os.path.exists(qr_path)

    result = f"""Public Key tìm được:
Email: {email}
Ngày tạo: {created_at}
Hết hạn: {expire_at} ({status})
Public Key (base64): {public_key_b64}
QR Code: {"Có" if has_qr else "Không có"}
"""

    write_log(email, "FindPublicKey", "Success")

    return True, (result, qr_path if has_qr else None)
