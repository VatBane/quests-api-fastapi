from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from v1.database.config import DBSettings


engine = create_async_engine(DBSettings().url)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session
