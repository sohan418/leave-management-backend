from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from .config import settings

# Example database_url in settings:
# settings.database_url = "mysql+aiomysql://user:password@localhost:3306/mydb"

# Async engine for MySQL (using aiomysql)
engine = create_async_engine(settings.database_url, echo=True, future=True)

# Sync engine (optional, for migrations or admin tasks)
sync_engine = create_engine(
    settings.database_url.replace("aiomysql", "pymysql"),
    echo=True,
    future=True
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI (async session)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Utility to create tables
async def create_tables():
    """Create all tables in the database (async)."""
    from ..models import user, employee, leave, attendance, overtime, client, invoice, master_data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
