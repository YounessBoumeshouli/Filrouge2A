from fastapi import APIRouter, Depends, Header
from app.core.exceptions import AppException
import re
from app.core.database import get_db
from app.schemas.user import UserCreate, LoginRequest, Token
from sqlalchemy.orm import Session
from app.services.user_service import Create_user, get_user_by_email, get_user_by_id
from app.services.auth_service import authenticate_user
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def validate_password(password):
    if len(password) < 8:
        raise AppException("Le mot de passe doit contenir au moins 8 caractères")
    if not re.search(r"[A-Z]", password):
        raise AppException("Le mot de passe doit contenir une majuscule")
    if not re.search(r"[a-z]", password):
        raise AppException("Le mot de passe doit contenir une minuscule")
    if not re.search(r"[0-9]", password):
        raise AppException("Le mot de passe doit contenir un chiffre")


@router.post("/register", response_model=Token)
def register(request: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise AppException("Utilisateur déjà existant")
    validate_password(request.password)
    Create_user(db, request)
    token = authenticate_user(db, request.email, request.password)
    return token


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    token = authenticate_user(db, request.email, request.password)
    if not token:
        raise AppException("Email ou mot de passe incorrect")
    return token


@router.get("/me")
def read_users_me(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise AppException("Token manquant")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise AppException("Token invalide")
        user = get_user_by_id(db, int(user_id))
        if not user:
            raise AppException("Utilisateur non trouvé")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": str(user.created_at),
        }
    except JWTError:
        raise AppException("Token invalide ou expiré")
