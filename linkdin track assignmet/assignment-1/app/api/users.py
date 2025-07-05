from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.database import get_db

router = APIRouter()

@router.get('/profile')
async def get_profile(request: Request):
    user = request.session.get('user')
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE google_id = ?", (user['google_id'],))
        row = cursor.fetchone()

        if not row:
            return JSONResponse(status_code=404, content={"error": "User not found"})

        user_data = dict(row)
        return JSONResponse({"user": user_data})

@router.get('/users')
async def list_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        users = [dict(row) for row in rows]
        return {"users": users, "count": len(users)}
