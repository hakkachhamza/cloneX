import asyncio
import sys

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.config import get_settings

settings = get_settings()


async def reset_admin() -> None:
    async with AsyncSessionLocal() as session:
        email = settings.first_superuser_email
        password = settings.first_superuser_password

        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user:
            print(f"Creating admin user: {email}")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name="Administrator",
                is_superuser=True,
                is_active=True,
            )
            session.add(user)
        else:
            print(f"Resetting admin user: {email}")
            user.hashed_password = get_password_hash(password)
            user.is_active = True
            user.is_superuser = True

        await session.commit()
        print("Admin user ready.")


if __name__ == "__main__":
    try:
        asyncio.run(reset_admin())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
