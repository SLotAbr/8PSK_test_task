from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = "sqlite+aiosqlite:///database.db"
engine = create_async_engine(DATABASE_URL)
AsyncSessionFactory = async_sessionmaker(
	engine, autocommit=False, expire_on_commit=False
)

async def getAsyncSession() -> AsyncGenerator[AsyncSession, None]:
	async with AsyncSessionFactory() as session:
		yield session
