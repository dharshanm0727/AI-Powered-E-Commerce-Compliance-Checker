from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_admin
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.auth import UserOut, UserUpdate
from app.schemas.report import AuditLogOut

router = APIRouter()

@router.get(
    "/",
    response_model=List[UserOut],
    summary="List All Users (Admin)",
    description="Retrieve a paginated list of all users. Requires administrator privileges.",
)
def read_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get User By ID (Admin)",
    description="Get details of a specific user by their ID. Requires administrator privileges.",
)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserOut,
    summary="Update User (Admin)",
    description="Update a specific user's details including roles and status. Requires administrator privileges.",
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if hasattr(user_in, 'email') and user_in.email is not None and user_in.email != user.email:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already registered by another user"
            )
        user.email = user_in.email
    
    if hasattr(user_in, 'full_name') and user_in.full_name is not None:
        user.full_name = user_in.full_name
    
    if hasattr(user_in, 'role') and getattr(user_in, 'role') is not None:
        user.role = user_in.role
    
    if hasattr(user_in, 'is_active') and getattr(user_in, 'is_active') is not None:
        user.is_active = user_in.is_active

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    response_model=UserOut,
    summary="Deactivate User (Admin)",
    description="Soft-delete a user by setting their is_active status to False. Requires administrator privileges.",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get(
    "/{user_id}/audit-logs",
    response_model=List[AuditLogOut],
    summary="Get User Audit Logs (Admin)",
    description="Get the audit logs for a specific user. Requires administrator privileges.",
)
def read_user_audit_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).offset(skip).limit(limit).all()
    return logs
