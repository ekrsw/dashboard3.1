from sqlalchemy import Column, String, UniqueConstraint

from app.models.db import BaseDatabase

class Group(BaseDatabase):
    __tablename__ = "group"
    name = Column(String)
    UniqueConstraint(name)