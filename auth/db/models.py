from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users_tracker'
    id = Column(Integer, primary_key=True)
    email =  Column(String(200), unique=True)
    full_name = Column(String(200))
    role = Column(String(200))
    active = Column(Boolean)
    public_id = Column(String(200), unique=True)
    position = Column(String(200))
    hashed_password = Column(String(256))
