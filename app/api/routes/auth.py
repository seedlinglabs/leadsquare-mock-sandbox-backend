from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.core.dependencies import get_current_user
from app.crud.user import user_crud
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MeResponse,
    UserInfo,
)
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = await user_crud.get_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error": {
                    "code": "CONFLICT",
                    "message": "Email already registered",
                },
            },
        )

    # Parse full_name into first_name and last_name
    name_parts = request.full_name.strip().split(maxsplit=1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else None

    # Create user using the UserCreate schema
    from app.schemas.user import UserCreate

    user_data = UserCreate(
        email=request.email,
        password=request.password,
        first_name=first_name,
        last_name=last_name,
    )

    user = await user_crud.create(db, user_data)

    return RegisterResponse(
        success=True,
        message="User registered successfully",
        user=UserInfo(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        ),
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login user"""
    user = await user_crud.authenticate(db, request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Incorrect email or password",
                },
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": "User account is inactive",
                },
            },
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        success=True,
        token=access_token,
        user=UserInfo(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        ),
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should delete token)"""
    return LogoutResponse(
        success=True,
        message="Logged out successfully",
    )


@router.get("/me", response_model=MeResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return MeResponse(
        success=True,
        user=UserInfo(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
        ),
    )
