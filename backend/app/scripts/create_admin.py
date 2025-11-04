#!/usr/bin/env python3
"""
Create admin user script
Run this to create the first admin user
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User, UserRole, UserStatus


async def create_admin():
    """Create admin user if it doesn't exist"""
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin already exists
            result = await db.execute(
                select(User).where(User.email == settings.FIRST_ADMIN_EMAIL)
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print(f"Admin user '{settings.FIRST_ADMIN_EMAIL}' already exists")
                return
            
            # Create admin user
            admin = User(
                email=settings.FIRST_ADMIN_EMAIL,
                password_hash=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                balance=0.00,
                first_name="Admin",
                last_name="User"
            )
            
            db.add(admin)
            await db.commit()
            
            print(f"✓ Admin user created successfully!")
            print(f"  Email: {settings.FIRST_ADMIN_EMAIL}")
            print(f"  Password: {settings.FIRST_ADMIN_PASSWORD}")
            print(f"  ⚠️  Please change the password after first login!")
        
        except Exception as e:
            print(f"Error creating admin user: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_admin())
