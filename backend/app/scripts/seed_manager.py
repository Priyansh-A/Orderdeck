import asyncio
from sqlmodel import select
from ..database import AsyncSessionLocal
from ..models import User
from ..permissions import UserRole
from ..utils import password_hash
from ..config import settings

async def seed_initial_manager():
    """Seed the initial manager user if no users exist"""
    
    async with AsyncSessionLocal() as session:
        query = select(User)
        result = await session.exec(query)
        existing_users = result.all()
        
        if existing_users:
            print("Users already exist")
            return
                
        hashed_password = password_hash.hash(settings.PASSWORD)
        
        manager_user = User(
            username=settings.USERNAME,
            email=settings.EMAIL,
            password=hashed_password,
            role=UserRole.MANAGER.value,
            disabled=False
        )
        
        session.add(manager_user)
        await session.commit()
        

async def main():
    await seed_initial_manager()

if __name__ == "__main__":
    asyncio.run(main())