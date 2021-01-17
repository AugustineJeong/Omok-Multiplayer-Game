from sqlalchemy import Column, String, Integer, Date

from main.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    wins = Column(Integer)
    losses = Column(Integer)
    level = Column(Integer)

    def __init__(self, username, password, wins=0, losses=0, level=1):
        self.username = username
        self.password = password
        self.wins = wins
        self.losses = losses
        self.level = level