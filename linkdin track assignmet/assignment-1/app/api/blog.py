from fastapi import APIRouter, Depends
from app.schemas.blog import BlogRequest
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.services.email_sender import send_email_notification
from dotenv import load_dotenv
import os
load_dotenv()
router = APIRouter()

@router.post("/create-blog", tags=["Blogs"])
async def create_blog(data: BlogRequest, user=Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blogs (title, content, author_id, author_name)
            VALUES (?, ?, ?, ?)
        """, (data.title, data.content, user["id"], user["name"]))
        conn.commit()
    print(f"Blog created by {user['name']} with ID {user['id']}")
    send_email_notification(
        to_email=user["email"],
        subject="New Blog Created!",
        content=f"Hey, your blog '{data.title}' was created successfully 🚀"
    )
    print(f"the mail has been sent to {user['email']}")
    return {
        "message": "Blog created successfully!",
        "blog": {
            "title": data.title,
            "content": data.content,
            "author_id": user["id"],
            "author_name": user["name"]
        }
    }

@router.get("/blogs")
async def get_all_blogs():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.content, b.created_at, u.name as author_name
            FROM blogs b
            JOIN users u ON b.author_id = u.id
            ORDER BY b.created_at DESC
        """)
        rows = cursor.fetchall()
        blogs = [
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "author": row["author_name"],
                "created_at": row["created_at"]
            } for row in rows
        ]
        return {"count": len(blogs), "blogs": blogs}
