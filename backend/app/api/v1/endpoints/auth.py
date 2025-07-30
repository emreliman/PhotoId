from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

@router.post("/register")
async def register(user_data: UserRegister):
    """
    Kullanıcı kayıt endpoint'i
    """
    # TODO: Implement user registration
    return {"message": "User registration endpoint - to be implemented"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Kullanıcı giriş endpoint'i
    """
    # TODO: Implement user login
    return {"message": "User login endpoint - to be implemented"}

@router.post("/refresh")
async def refresh_token():
    """
    Token yenileme endpoint'i
    """
    # TODO: Implement token refresh
    return {"message": "Token refresh endpoint - to be implemented"} 