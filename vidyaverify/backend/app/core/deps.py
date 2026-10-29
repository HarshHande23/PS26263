from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.core.enums import UserRole
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raw_token = token or request.query_params.get("token")
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(raw_token)
    if not payload:
        raise credentials_exception
    if payload.get("type") != "access":
        raise credentials_exception
    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_roles(*roles: UserRole):
    """Dependency factory that enforces role-based access."""
    def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user
    return _checker


def require_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
    return require_roles(UserRole.SUPER_ADMIN)(current_user)


def require_aicte_or_above(current_user: User = Depends(get_current_active_user)) -> User:
    return require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN)(current_user)


def require_college_or_above(current_user: User = Depends(get_current_active_user)) -> User:
    allowed = [
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN,
        UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF,
    ]
    return require_roles(*allowed)(current_user)
