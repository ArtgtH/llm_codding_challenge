from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from configs.config import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=False,
)

session_factory = sessionmaker(engine)

Base = declarative_base()
