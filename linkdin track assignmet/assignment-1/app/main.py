from fastapi import FastAPI
from app.database import init_db
from app.api import auth, users, blog
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import os


load_dotenv()

app = FastAPI(docs_url="/docs")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(blog.router)

@app.get("/")
def home():
    return {"msg": "Welcome! Visit /login to visi the assignment-1 ."}
