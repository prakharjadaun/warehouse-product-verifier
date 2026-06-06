"""
Run once to create the first admin user.

Usage:
    python seed_admin.py
    python seed_admin.py --email custom@example.com --password mypassword
"""
import argparse
import asyncio

from sqlalchemy import select

from app.database import async_session_factory
from app.models.user import User, UserRole
from app.services.auth_service import hash_password


async def seed(email: str, password: str, full_name: str) -> None:
    async with async_session_factory() as session:
        existing = await session.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            print(f"User {email} already exists.")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole.admin,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin created: {email}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default="admin@warehouse.com")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--name", default="System Admin")
    args = parser.parse_args()
    asyncio.run(seed(args.email, args.password, args.name))
