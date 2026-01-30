from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.crud.user import user_crud
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_crud.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return await user_crud.create(db, user_data)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    return await user_crud.get_all(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    user = await user_crud.update(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await user_crud.delete(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
