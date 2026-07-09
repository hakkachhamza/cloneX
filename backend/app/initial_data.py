import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.config import get_settings

settings = get_settings()


async def create_initial_data() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == settings.first_superuser_email)
        )
        user = result.scalars().first()
        if not user:
            user = User(
                email=settings.first_superuser_email,
                hashed_password=get_password_hash(settings.first_superuser_password),
                full_name="Administrator",
                is_superuser=True,
                is_active=True,
            )
            session.add(user)
            await session.commit()
            print(f"Created initial superuser: {settings.first_superuser_email}")


if __name__ == "__main__":
    asyncio.run(create_initial_data())
