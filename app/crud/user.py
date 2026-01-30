from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
import hashlib

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def hash_password(password: str) -> str:
    """Simple password hashing - use bcrypt in production"""
    return hashlib.sha256(password.encode()).hexdigest()


class UserCRUD:
    async def create(self, db: AsyncSession, user_data: UserCreate) -> User:
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get(self, db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        user = await self.get(db, user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    async def delete(self, db: AsyncSession, user_id: int) -> bool:
        user = await self.get(db, user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()
        return True


user_crud = UserCRUD()
