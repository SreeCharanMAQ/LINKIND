from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import decode_jwt_token

security = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = decode_jwt_token(token.credentials)
        return {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "name": payload.get("name")
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
