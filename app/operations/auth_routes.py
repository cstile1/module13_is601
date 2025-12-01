#app/operations/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.auth.jwt import (
    verify_password,
    get_password_hash,
    create_token
)
from app.schemas.token import TokenType

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    # Check duplicate email
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_pw = get_password_hash(payload.password)

    # Create user
    user = User(
        email=payload.email,
        username=payload.email,  # username = email
        hashed_password=hashed_pw,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("username")
    password = payload.get("password")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create JWT token
    access_token = create_token(
        user_id=str(user.id),
        token_type=TokenType.ACCESS
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
