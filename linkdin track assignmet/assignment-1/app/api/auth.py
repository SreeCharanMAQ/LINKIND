from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.auth.oauth_google import oauth
from app.auth.jwt_handler import create_jwt_token
from app.database import create_or_update_user
from app.database import create_or_update_user


router = APIRouter()

@router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)



@router.get('/auth')
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