"""Module for SQLAlchemy variables."""

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

__all__ = (
    'engine',
    'Base',
    'Session',
)

engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
Session = sessionmaker(bind=engine)
