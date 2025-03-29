from fastapi import APIRouter, HTTPException, status
from user_model import verify_user, create_user, user_exists
from user_schema import UserResponse
from pydantic import BaseModel

router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="Endpoint para registrar un nuevo usuario con nombre de usuario y contraseña"
)
async def register_user(username: str, password: str):
    """
    Registrar un nuevo usuario

    Parámetros:
    - username: Nombre de usuario (debe ser único)
    - password: Contraseña del usuario
    """
    if user_exists(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    try:
        create_user(username, password)
        return {
            "message": "Usuario registrado exitosamente",
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )
# Define un modelo para los datos de inicio de sesión
class UserLogin(BaseModel):
    username: str
    password: str

# Luego modifica tu endpoint para usar el modelo `UserLogin`:
@router.post(
    "/login",
    response_model=UserResponse,
    summary="Verificar credenciales",
    description="Endpoint para verificar nombre de usuario y contraseña"
)
async def login_user(credentials: UserLogin):  # Usa el modelo UserLogin aquí
    """
    Verifica credenciales de usuario
    
    Parámetros:
    - username: Nombre de usuario
    - password: Contraseña
    """
    if verify_user(credentials.username, credentials.password):
        return {
            "message": "Credenciales válidas",
            "success": True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
