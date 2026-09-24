from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MongoDB:
    client = None
    db = None


mongodb = MongoDB()


async def connect_mongodb():
    pass


async def close_mongodb():
    pass


class RedisClient:
    client = None


redis_client = RedisClient()


async def connect_redis():
    pass


async def close_redis():
    pass


class Neo4jClient:
    driver = None


neo4j_client = Neo4jClient()


def connect_neo4j():
    pass


def close_neo4j():
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongodb():
    return None


def get_redis():
    return None


def get_neo4j():
    return None