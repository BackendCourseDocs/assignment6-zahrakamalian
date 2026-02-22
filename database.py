import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

# اگر async می‌خوای از این استفاده کن:
# from sqlmodel.ext.asyncio.session import AsyncSession
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL در .env نیست")

# sync (ساده‌تر برای شروع)
# echo=True → sqlها رو نشون می‌ده (برای دیباگ)
engine = create_engine(DATABASE_URL, echo=True)

# اگر async می‌خوای:
# engine = create_async_engine(DATABASE_URL, echo=True)
# async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# برای async:
# async def get_session() -> AsyncSession:
#     async with async_session() as session:
#         yield session
