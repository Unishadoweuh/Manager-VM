#!/usr/bin/env python3
"""
Seed database with sample data
"""

import asyncio
from decimal import Decimal

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.models.template import VMTemplate


async def seed_db():
    """Seed database with sample data"""
    
    async with AsyncSessionLocal() as db:
        try:
            print("Seeding database...")
            
            # Create sample templates
            templates = [
                VMTemplate(
                    name="Ubuntu 22.04 - Small",
                    description="Ubuntu 22.04 LTS with 2 CPU cores and 2GB RAM",
                    cpu_cores=2,
                    ram_mb=2048,
                    disk_gb=20,
                    os_type="linux",
                    os_name="Ubuntu 22.04 LTS",
                    cost_per_hour=Decimal("0.05"),
                    is_public=True,
                    is_active=True,
                    tags="ubuntu,linux,small"
                ),
                VMTemplate(
                    name="Ubuntu 22.04 - Medium",
                    description="Ubuntu 22.04 LTS with 4 CPU cores and 4GB RAM",
                    cpu_cores=4,
                    ram_mb=4096,
                    disk_gb=40,
                    os_type="linux",
                    os_name="Ubuntu 22.04 LTS",
                    cost_per_hour=Decimal("0.10"),
                    is_public=True,
                    is_active=True,
                    tags="ubuntu,linux,medium"
                ),
                VMTemplate(
                    name="Windows Server 2022",
                    description="Windows Server 2022 with 4 CPU cores and 8GB RAM",
                    cpu_cores=4,
                    ram_mb=8192,
                    disk_gb=60,
                    os_type="windows",
                    os_name="Windows Server 2022",
                    cost_per_hour=Decimal("0.20"),
                    is_public=True,
                    is_active=True,
                    tags="windows,server"
                ),
                VMTemplate(
                    name="Debian 12 - Small",
                    description="Debian 12 with 1 CPU core and 1GB RAM",
                    cpu_cores=1,
                    ram_mb=1024,
                    disk_gb=15,
                    os_type="linux",
                    os_name="Debian 12",
                    cost_per_hour=Decimal("0.02"),
                    is_public=True,
                    is_active=True,
                    tags="debian,linux,small,budget"
                ),
            ]
            
            for template in templates:
                db.add(template)
            
            # Create test user (if not exists)
            test_user = User(
                email="user@example.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                balance=Decimal("50.00"),
                first_name="Test",
                last_name="User"
            )
            db.add(test_user)
            
            await db.commit()
            
            print("✓ Database seeded successfully!")
            print(f"  - Created {len(templates)} VM templates")
            print(f"  - Created test user: user@example.com / password123")
        
        except Exception as e:
            print(f"Error seeding database: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(seed_db())
