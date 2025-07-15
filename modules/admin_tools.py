# Chức năng 10: Phân quyền, khóa/mở tài khoản, xem toàn bộ log
import json, os
from datetime import datetime
from modules.logger import write_log

USER_FILE = "data/users.json"
LOG_FILE = "data/security.log"

# Xác minh quyền admin
def is_admin(email):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
    return users.get(email, {}).get("role") == "admin"

# Xem danh sách người dùng
def view_all_users(admin_email):
    if not os.path.exists(USER_FILE):
        return True, "Không tìm thấy dữ liệu người dùng."
    
    with open(USER_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
        
    info_list = []

    # Hiển thị danh sách người dùng dạng "STT - email - Họ tên - Role - Trạng thái" theo bảng
    info_list.append("STT - email - Họ tên - Role - Trạng thái")
    info_list.append("-" * 60)
    for i, (email, info) in enumerate(users.items(), start=1):
        status = "Đang khóa" if info.get("is_locked", False) else "Đang hoạt động"
        # info_str format: STT - email - Họ tên - Role - Trạng thái
        info_str = f"{i} - {email} - {info.get('name', 'Chưa cập nhật')} - {info.get('role', 'user')} - {status}"
        info_list.append(info_str)
    write_log(admin_email, "AdminViewUsers", f"Xem {len(users)} người dùng")
    return True, "\n".join(info_list)

    # Hiển thị danh sách người dùng dạng "STT - email - Họ tên - Role - Trạng thái" theo dạng bảng excel
           


    # for email, info in users.items():
    #     status = "Đang khóa" if info.get("is_locked", False) else "Đang hoạt động"
    #     # info_str format: STT - email - Họ tên - Role - Trạng thái
    #     info_str = f"{len(info_list) + 1} - {email} - {info.get('name', 'Chưa cập nhật')} - {info.get('role', 'user')} - {status}"
    #     info_list.append(info_str)
    # write_log(admin_email, "AdminViewUsers", f"Xem {len(users)} người dùng")
    # return True, "\n".join(info_list) 

# Khóa hoặc mở khóa tài khoản
def toggle_user_account(target_email, action):
    if not os.path.exists(USER_FILE):
        return False, "Không tìm thấy dữ liệu người dùng."
    
    with open(USER_FILE, "r", encoding="utf-8") as f:   
        users = json.load(f)
        
    if target_email not in users:
        return False, "Không tìm thấy người dùng này."
    
    if action == "lock":
        users[target_email]["is_locked"] = True
    elif action == "unlock":
        users[target_email]["is_locked"] = False 
        # Nếu đang bị khóa tạm thời, xóa thời gian khóa tạm
        if "temp_lock_time" in users[target_email]:
            users[target_email].pop("temp_lock_time", None)
            users[target_email]["login_attempts"] = 0  # Reset attempts
    else:
        return False, "Hành động không hợp lệ."

    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
        
    write_log(target_email, f"Admin{action.capitalize()}User", f"{action.capitalize()} tài khoản {target_email}")
    return True, f"Tài khoản {target_email} đã được {action} thành công."

# Xem log hệ thống
def view_system_logs(admin_email):
    if not os.path.exists(LOG_FILE):
        return False, "Không tìm thấy log hệ thống."

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    latest_logs = lines[-50:] if len(lines) > 50 else lines
    log_text = "".join(latest_logs)

    write_log(admin_email, "AdminViewLog", "Đã xem log hệ thống")
    return True, log_text
