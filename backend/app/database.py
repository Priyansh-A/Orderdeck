from typing import Annotated
from fastapi import Depends 
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True, 
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            
SessionDep = Annotated[AsyncSession, Depends(get_session)]
