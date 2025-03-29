from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Modelos para usuarios
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    email: EmailStr
    fecha_registro: datetime

# Modelos para caudalímetros
class Medicion(BaseModel):
    caudal: float
    consumo_total: float
    temperatura: Optional[float] = None
    evento_fuga: bool

class Caudalimetro(BaseModel):
    nombre: str
    tipo: str
    estado: str
    mediciones: List[Medicion]

class AnalisisRequest(BaseModel):
    user_id: str