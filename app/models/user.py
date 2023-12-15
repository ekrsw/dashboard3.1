from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey

from app.models.db import BaseDatabase

class User(BaseDatabase):
    __tablename__ = "user"
    employee_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    UniqueConstraint(username)
    reporter_name = Column(String)
    UniqueConstraint(reporter_name)
    sweet_name = Column(String)
    UniqueConstraint(sweet_name)
    group_id = Column(ForeignKey("group.id", ondelete="CASCADE"))
