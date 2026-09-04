from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.auth import Token, UserCreate, UserUpdate, UserOut, PasswordChange, RefreshTokenRequest

router = APIRouter()


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Register a new user in the system. Returns access and refresh tokens.",
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role or "user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    audit_log = AuditLog(
        user_id=user.id,
        action="REGISTER",
        entity_type="User",
        entity_id=user.id,
        details={"email": user.email}
    )
    db.add(audit_log)
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, roles=user.role, expires_delta=access_token_expires)
    refresh_token = create_access_token(user.id, roles=user.role, expires_delta=timedelta(days=7))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id
    }


@router.post(
    "/login",
    response_model=Token,
    summary="User Login",
    description="OAuth2 compatible token login, returns access and refresh tokens.",
)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    audit_log = AuditLog(
        user_id=user.id,
        action="LOGIN",
        entity_type="User",
        entity_id=user.id,
        details={"email": user.email}
    )
    db.add(audit_log)
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user.id, roles=user.role, expires_delta=access_token_expires)
    refresh_token = create_access_token(user.id, roles=user.role, expires_delta=timedelta(days=7))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id
    }


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh Token",
    description="Generate a new access token using a valid refresh token.",
)
def refresh_token_endpoint(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Any:
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or not found")

    access_token = create_access_token(user.id, roles=user.role, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh_token = create_access_token(user.id, roles=user.role, expires_delta=timedelta(days=7))

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id
    }


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get Current User Profile",
    description="Get profile information of the currently authenticated user.",
)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    return current_user


@router.put(
    "/me",
    response_model=UserOut,
    summary="Update Current User Profile",
    description="Update profile information of the currently authenticated user.",
)
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    if user_in.email is not None and user_in.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already registered by another user"
            )
        current_user.email = user_in.email
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post(
    "/change-password",
    response_model=UserOut,
    summary="Change Password",
    description="Change password of the currently authenticated user.",
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
