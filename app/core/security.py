""" security.py berisikan fungsi untuk menghandle hashing password user bcrypt"""

from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    #buat mastikan password 32 bytes sebelum di-hash
    sha = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(sha)

def verify_password(plain:str, hashed: str) -> bool:
    sha = hashlib.sha256(plain.encode('utf-8')).hexdigest()
    return pwd_context.verify(sha, hashed)

