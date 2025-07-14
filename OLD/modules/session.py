current_user = {}

def set_user(email, passphrase=None, role="user"):
    global current_user
    current_user = {
        "email": email.lower().strip(),
        "passphrase": passphrase,  
        "role": role
    }
    
def get_user():
    return current_user

def get_email():
    return current_user.get("email", "").lower().strip()

def get_passphrase():
    return current_user.get("passphrase")

def get_role():
    return current_user.get("role", "user")

def clear_session():
    global current_user
    current_user = {}