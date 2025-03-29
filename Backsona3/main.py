from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
import google.generativeai as genai
from schemas import *

# Configuración inicial
load_dotenv()
app = FastAPI()

# Configuración de Uvicorn
UVICORN_CONFIG = {
    "host": os.getenv("HOST", "0.0.0.0"),  # Escucha en todas las interfaces
    "port": int(os.getenv("PORT", 8000)),   # Puerto por defecto: 8000
    "reload": os.getenv("RELOAD", "True") == "True",  # Recarga automática (solo desarrollo)
    "workers": int(os.getenv("WORKERS", "1")),  # Número de workers (1 para desarrollo)
}

# MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["agua_db"]
users_collection = db["users"]

# Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Autenticación JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Funciones de autenticación
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# Endpoints de usuarios
@app.post("/registro", response_model=UserOut)
async def registro(user: UserCreate):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "password": hashed_password,
        "fecha_registro": datetime.utcnow(),
        "caudalímetros": []  # Inicialmente vacío
    }
    result = users_collection.insert_one(user_data)
    return {**user.dict(), "fecha_registro": user_data["fecha_registro"]}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token = create_access_token(data={"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoints de caudalímetros
@app.get("/caudalimetros", response_model=List[Caudalimetro])
async def get_caudalimetros(user: dict = Depends(get_current_user)):
    return user.get("caudalímetros", [])

@app.get("/caudalimetros/{caudalimetro_id}", response_model=Caudalimetro)
async def get_caudalimetro(caudalimetro_id: str, user: dict = Depends(get_current_user)):
    try:
        caudal_oid = ObjectId(caudalimetro_id)
    except:
        raise HTTPException(status_code=400, detail="ID inválido")

    for caudal in user.get("caudalímetros", []):
        if caudal["_id"] == caudal_oid:
            return caudal

    raise HTTPException(status_code=404, detail="Caudalímetro no encontrado")

# Endpoint de recomendaciones (Gemini)
@app.post("/analisis")
async def generar_analisis(request: AnalisisRequest, user: dict = Depends(get_current_user)):
    if str(user["_id"]) != request.user_id:
        raise HTTPException(status_code=403, detail="No autorizado")

    caudalimetros = user.get("caudalímetros", [])
    if not caudalimetros:
        raise HTTPException(status_code=404, detail="No hay caudalímetros registrados")

    # Preparar datos para Gemini
    datos_para_gemini = {
        "caudalimetros": [
            {
                "nombre": c["nombre"],
                "consumo_total": sum(m["consumo_total"] for m in c["mediciones"]),
                "ultima_medicion": c["mediciones"][-1] if c["mediciones"] else None
            }
            for c in caudalimetros
        ]
    }

    prompt = f"""
    Eres un experto en gestión hídrica. Analiza estos datos de caudalímetros:
    {datos_para_gemini}

    ### Tareas:
    1. **Resumen de consumo**: Total por caudalímetro y comparativa con estándares.
    2. **Detección de anomalías**: ¿Fugas? ¿Consumo excesivo en algún punto?
    3. **Recomendaciones personalizadas**: Acciones concretas para reducir el consumo.

    ### Formato de respuesta (JSON):
    {{
        "resumen": "texto",
        "anomalias": ["lista"],
        "recomendaciones": ["lista"]
    }}
    """

    try:
        response = model.generate_content(prompt)
        return {"analisis": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=UVICORN_CONFIG["host"],
        port=UVICORN_CONFIG["port"],
        reload=UVICORN_CONFIG["reload"],
        workers=UVICORN_CONFIG["workers"],
    )