# Chức năng 8, 9: Ký số và xác minh chữ ký
import os, json, hashlib, base64
from datetime import datetime
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from modules.logger import write_log
from modules.account_manager import decrypt_private_key
from modules import session

USER_FILE = "data/users.json"
SIG_DIR = "data/signatures/"
os.makedirs(SIG_DIR, exist_ok=True)

# Ký số một file
def sign_file(file_path, email, passphrase):
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        digest = SHA256.new(content)

        # Lấy khóa người dùng
        with open(USER_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

        if email not in users or not users[email].get("rsa_keys"):
            return False, "Không tìm thấy khóa người dùng."

        enc_priv = users[email]["rsa_keys"]["private_key_encrypted"]
        ok, priv_bytes = decrypt_private_key(enc_priv, passphrase)
        if not ok:
            return False, "Không giải mã được khóa cá nhân."

        priv_key = RSA.import_key(priv_bytes)
        signer = pkcs1_15.new(priv_key)
        signature = signer.sign(digest)

        sig_data = {
            "email": email,
            "filename": os.path.basename(file_path),
            "signed_at": datetime.now().isoformat(),
            "signature": base64.b64encode(signature).decode()
        }

        sig_path = os.path.join(SIG_DIR, os.path.basename(file_path) + ".sig")
        with open(sig_path, "w", encoding="utf-8") as f:
            json.dump(sig_data, f, indent=2)

        write_log(email, "SignFile", f"Success - {file_path}")
        return True, f"Đã ký số và lưu tại: {sig_path}"
    except Exception as e:
        write_log(email, "SignFile", f"Failed - {str(e)}")
        return False, "Ký số thất bại."
    
# Xác minh chữ ký của một file
def verify_signature(file_path, sig_path):
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        digest = SHA256.new(content)

        with open(sig_path, "r", encoding="utf-8") as f:
            sig_data = json.load(f)

        signer_email = sig_data.get("email")
        signature = base64.b64decode(sig_data["signature"])
        signed_at = sig_data.get("signed_at", "Không rõ thời gian")
        
        print(f"Verifying signature for {file_path} by {signer_email} at {signed_at}")
        
        # Load public keys from users.json
        pubkeys = {}
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
                for email, info in users.items():
                    if "rsa_keys" in info and "public_key" in info["rsa_keys"]:
                        pubkeys[email] = base64.b64decode(info["rsa_keys"]["public_key"])
        else:
            write_log("UNKNOWN", "VerifySignature", "Failed - User file not found")
            return False, "Không tìm thấy dữ liệu người dùng."
            
        # check if the signer_email exists in pubkeys
        signer_key_data = pubkeys.get(signer_email)
        if signer_key_data:
            try:
                verifier = pkcs1_15.new(RSA.import_key(signer_key_data))
                verifier.verify(digest, signature)
                write_log(signer_email, "VerifySignature", "Success - Matched signer key")
                return True, f"Chữ ký hợp lệ.\nNgười ký: {signer_email}\nNgày ký: {signed_at}"
            except (ValueError, TypeError):
                pass

        # 2. Thử với tất cả public key khác
        for email, info in pubkeys.items():
            if email == signer_email:
                continue  
            try:
                # pub_key = RSA.import_key(base64.b64decode(info["public_key"]))
                verifier = pkcs1_15.new(RSA.import_key(info))
                verifier.verify(digest, signature)
                write_log(signer_email, "VerifySignature", f"Success - Matched other key ({email})")
                return True, f"Chữ ký hợp lệ với public key của {email}.\nNgười ký khai báo: {signer_email}\nNgày ký: {signed_at}"
            except (ValueError, TypeError):
                continue

        write_log(signer_email, "VerifySignature", "Failed - No matching public key")
        return False, "Chữ ký không hợp lệ. Không khớp với bất kỳ public key nào đã lưu."
    
    except Exception as e:
        write_log(signer_email if 'signer_email' in locals() else "UNKNOWN", "VerifySignature", f"Failed - Exception: {e}")
        return False, f"Lỗi xác minh chữ ký: {str(e)}"
