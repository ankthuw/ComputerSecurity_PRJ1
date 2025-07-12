# Chức năng 6, 7, 10, 16: Mã hóa file, giải mã, chia nhỏ file, tùy chọn định dạng
import os, json, base64
from datetime import datetime
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from modules.logger import write_log
from modules import rsa_key_manager

USER_FILE = "data/users.json"
ENC_DIR = "data/encrypted/"
# KEY_DIR = "data/keys/"
os.makedirs(ENC_DIR, exist_ok=True)

# Mã hóa file cho người nhận
def encrypt_file(sender_email, recipient_email, file_path, merge=True):
    if not os.path.exists(file_path):
        return False, "File không tồn tại hoặc đường dẫn không hợp lệ."
    if os.path.getsize(file_path) == 0:
        return False, "File rỗng, không thể mã hóa."
    
    with open(USER_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    if recipient_email not in users or not users[recipient_email].get("rsa_keys"):
        return False, "Người nhận chưa có public key."

    pubkey_b64 = users[recipient_email]["rsa_keys"]["public_key"]
    pubkey = RSA.import_key(base64.b64decode(pubkey_b64))
    rsa_cipher = PKCS1_OAEP.new(pubkey)

    with open(file_path, "rb") as f:
        raw = f.read()

    # Chia file nếu lớn hơn 5MB
    blocks = [raw[i:i+1024*1024] for i in range(0, len(raw), 1024*1024)]

    encrypted_blocks = [] 
    session_key = get_random_bytes(32) # AES-256 key

    for block in blocks:
        cipher = AES.new(session_key, AES.MODE_GCM)
        ct, tag = cipher.encrypt_and_digest(block)
        encrypted_blocks.append({
            "nonce": base64.b64encode(cipher.nonce).decode(),
            "tag": base64.b64encode(tag).decode(),
            "ciphertext": base64.b64encode(ct).decode()
        })

    encrypted_session_key = rsa_cipher.encrypt(session_key)
    # Metadata
    metadata = {
        "sender": sender_email,
        "recipient": recipient_email,
        "timestamp": datetime.now().isoformat(),
        "filename": os.path.basename(file_path)
    }
    
    # filename = os.path.basename(file_path)

    if merge:
        enc_file = {
            "metadata": metadata,
            "encrypted_session_key": base64.b64encode(encrypted_session_key).decode(),
            "blocks": encrypted_blocks
        }
        output_path = f"{ENC_DIR}/{metadata['filename']}.enc"
        with open(output_path, "w") as f:
            json.dump(enc_file, f)
        write_log(sender_email, "EncryptFile", f"Success - merged to {output_path}")
        return True, f"Mã hóa thành công (gộp): {output_path}"
    else:
        # Save key separately
        key_path = f"{ENC_DIR}/{metadata['filename']}.key"
        data_path = f"{ENC_DIR}/{metadata['filename']}.enc"
        with open(key_path, "wb") as f:
            f.write(encrypted_session_key)
        with open(data_path, "w") as f:
            json.dump({
                "metadata": metadata,
                "blocks": encrypted_blocks
            }, f)
        write_log(sender_email, "EncryptFile", f"Success - split to {data_path} and {key_path}")
        return True, f"Mã hóa thành công (tách): {data_path}, {key_path}"

# Giải mã file
def decrypt_file(recipient_email, passphrase, enc_path, key_path=None):
    if not os.path.exists(enc_path):
        return False, "Không tìm thấy file mã hóa (.enc)."

    with open(USER_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    user = users.get(recipient_email)
    if not user or not user.get("rsa_keys"):
        return False, "Người dùng không tồn tại hoặc chưa có khóa."

    # Giải mã private key
    from modules.account_manager import decrypt_private_key
    enc_data = user["rsa_keys"]["private_key_encrypted"]
    ok, priv_bytes = decrypt_private_key(enc_data, passphrase)
    if not ok:
        return False, "Sai passphrase hoặc không giải mã được private key."

    privkey = RSA.import_key(priv_bytes)
    rsa_cipher = PKCS1_OAEP.new(privkey)

    # Đọc file mã hóa
    try:
        with open(enc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return False, "Không thể đọc file mã hóa. Định dạng không hợp lệ."
    
    if "metadata" not in data or "blocks" not in data:
        return False, "File mã hóa không đúng định dạng."
    
    is_merged = "encrypted_session_key" in data
    if is_merged:
        encrypted_session_key = base64.b64decode(data["encrypted_session_key"])
    elif key_path:
        if not os.path.isfile(key_path):
            return False, "Không tìm thấy file khóa riêng tư (.key)."
        with open(key_path, "rb") as f:
            encrypted_session_key = f.read()
    else:
        return False, "Không có khóa riêng tư để giải mã. Cần cung cấp file khóa."
    
    try:
        session_key = rsa_cipher.decrypt(encrypted_session_key)
    except Exception as e:
        write_log(recipient_email, "DecryptFile", f"Fail - RSA Decrypt Error: {e}")
        return False, f"Không thể giải mã khóa phiên.\nChi tiết: {e}"
    
    decrypted = b""
    try:
        for block in data["blocks"]:
            cipher = AES.new(session_key, AES.MODE_GCM, nonce=base64.b64decode(block["nonce"]))
            ct = base64.b64decode(block["ciphertext"])
            tag = base64.b64decode(block["tag"])
            decrypted += cipher.decrypt_and_verify(ct, tag)
    except Exception:
        write_log(recipient_email, "DecryptFile", f"Fail - AES Decrypt Error: {e}")
        return False, "Không giải mã được nội dung file (AES GCM thất bại)"

    out_path = f"{ENC_DIR}/decrypted_{data['metadata']['filename']}"
    with open(out_path, "wb") as f:
        f.write(decrypted)

    write_log(recipient_email, "DecryptFile", f"Success - decrypted to {out_path}")
    return True, f"Đã giải mã. Lưu tại: {out_path}"
