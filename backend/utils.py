from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash(password: str):
    return password_hash(password)

def verify(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)
