from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.auth.oauth_google import oauth
from app.auth.jwt_handler import create_jwt_token
from app.database import create_or_update_user, get_db
from app.schemas.LoginUser import LoginUser
from app.schemas.RegisterUser import RegisterUser
import sqlite3
import hashlib
import secrets



router = APIRouter()

def hash_password(password: str) -> str:
    """Hash a password using a random salt"""
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + password_hash.hex()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against its hash"""
    if not stored_hash or len(stored_hash) < 64:
        return False
    salt = stored_hash[:64]
    stored_password_hash = stored_hash[64:]
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return password_hash.hex() == stored_password_hash



@router.get('/googlelogin',tags=["Googleauth"])
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)



@router.get('/auth' , tags=["Googleauth"])
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        
        userinfo_response = await oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo', token=token)
        user = userinfo_response.json()
        
        # Store user data in database
        google_id = user.get("sub")  # Google's unique user ID
        name = user.get("name")
        email = user.get("email")
        picture = user.get("picture")
        
        if not google_id or not email:
            return JSONResponse(
                status_code=400,
                content={"error": "Required user information not available"}
            )
        
       
        user_id = create_or_update_user(google_id, name, email, picture)
        
       
        request.session['user'] = {
            'id': user_id,
            'google_id': google_id,
            'name': name,
            'email': email,
            'picture': picture
        }
        jwt_token = create_jwt_token({
            "user_id": user_id,
            "email": email,
            "name": name
        })
        
        return JSONResponse({
            "message": "Login successful via Google!",
            "token": jwt_token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "picture": picture
            }
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Authentication failed: {str(e)}"}
        )
    


@router.post("/register", tags=["Login"])
def register_user(user: RegisterUser):
    with get_db() as conn:
        cursor = conn.cursor()
        password_hash = hash_password(user.password)

        try:
            cursor.execute("""
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
            """, (user.name, user.email, password_hash))
            conn.commit()
            return {"msg": "User registered successfully 🚀"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already registered 💀")

@router.post("/login" ,tags=["Login"])
def login_user(user: LoginUser):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
        db_user = cursor.fetchone()

        if not db_user or not db_user["password_hash"]:
            raise HTTPException(status_code=401, detail="User not found ya invalid login 🧨")

        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Wrong password bro 🧢")

        token = create_jwt_token({"user_id": db_user["id"], "email": db_user["email"]})
        return {"access_token": token, "token_type": "bearer"}
