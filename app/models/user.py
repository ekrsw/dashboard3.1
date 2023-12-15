import datetime as dt

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy import create_engine
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

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    employee_id = Column(Integer)
    UniqueConstraint(employee_id)
    name = Column(String)
    UniqueConstraint(name)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)