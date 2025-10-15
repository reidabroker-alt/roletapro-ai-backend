# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base

from .routers import auth, users, simulator, chat

# Criar as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RoletaPro.AI API", version="2.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(simulator.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API RoletaPro.AI v2.0"}

