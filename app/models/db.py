import datetime

from sqlalchemy import Column, Integer, String, DateTime, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

class Database(object):
    def __init__(self):
        self.engine = create_engine(f"sqlite:///{settings.DB_NAME}")
        self.session = self.connect_db()
    
    def connect_db(self):
        Base.metadata.create_all(self.engine)
        session = sessionmaker(self.engine)
        return session()

Base = declarative_base()
database = Database()

class BaseDatabase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    UniqueConstraint(name)
    create_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
