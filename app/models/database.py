import datetime as dt

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import settings


class Database(object):
    def __init__(self) -> None:
        self.engine = create_engine(f"sqlite:///{settings.DB_NAME}")
        self.connect_db()

    def connect_db(self) -> sessionmaker:
        Base.metadata.create_all(self.engine)
        session = sessionmaker(self.engine)
        return session()



Base = declarative_base()
database = Database()


class TodaysKpi(Base):
    __tablename__ = "todays_kpi"
    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(DateTime, nullable=False)
    kpi_direct_1g = Column(String, nullable=False)
    kpi_20_2g = Column(String, nullable=False)
    kpi_40_3g = Column(String, nullable=False)
    kpi_40_n = Column(String, nullable=False)
