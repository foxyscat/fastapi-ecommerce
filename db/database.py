from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine,AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from contextlib import asynccontextmanager

# Define the database URL using SQLite with aiosqlite for asynchronous operations
SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///../db/test.db'

# Create an asynchronous engine bound to the database URL
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)  # Added echo=True for debugging purposes

# Create a session factory using the asynchronous engine
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Define a base class for ORM models using DeclarativeBase and MappedAsDataclass
class Base(DeclarativeBase, MappedAsDataclass):
    pass

# Define an asynchronous context manager for obtaining a database session
@asynccontextmanager
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
