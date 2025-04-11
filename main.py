"""
Основний модуль застосунку FastAPI для управління контактами.

Цей модуль містить налаштування CORS та підключення роутерів API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import contacts, utils, auth, users

app = FastAPI(title="Contacts API")

origins = [
    "http://localhost:3000",  
    "http://localhost:8000", 
    "http://127.0.0.1:8000" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
async def root():
    """
    Кореневий ендпоінт API.
    
    Returns:
        dict: Привітальне повідомлення та інструкції для користувача.
    """
    return {"message": "Welcome to Contacts API! Go to /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 