from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="API de Registro de Usuarios",
    description="API para registrar usuarios en MongoDB Atlas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api", tags=["Autenticación"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplaza * con tu URL de la app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)