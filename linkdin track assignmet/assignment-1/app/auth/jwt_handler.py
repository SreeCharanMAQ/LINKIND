import jwt
from datetime import datetime, timedelta
import os

SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")

def create_jwt_token(data: dict, expires_in: int = 3600):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(seconds=expires_in)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm="HS256")

def decode_jwt_token(token: str):
    return jwt.decode(token, SECRET, algorithms=["HS256"])
