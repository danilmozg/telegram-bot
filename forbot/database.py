from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv('DATABASE_URL', "postgresql+asyncpg://bot_user:default_password@postgres:5432/bot_db")
print(f"Using DATABASE_URL: {DATABASE_URL}")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("init_db completed successfully")
    except Exception as e:
        print(f"Ошибка подключения к базе: {e}")
        raise
