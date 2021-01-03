from sqlalchemy import Column, String, Integer, Date

from main.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    level = Column(Integer)

    def __init__(self, username, password, level=1):
        self.username = username
        self.password = password
        self.level = level