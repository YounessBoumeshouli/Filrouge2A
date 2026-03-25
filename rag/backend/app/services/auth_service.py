from sqlalchemy.orm import Session
from app.models.user import Users
from app.core.security import verify_password, create_access_token,create_refresh_token

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(Users).filter(Users.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }