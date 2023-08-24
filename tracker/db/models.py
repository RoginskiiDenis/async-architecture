from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email =  Column(String(200), unique=True)
    full_name = Column(String(200))
    role = Column(String(200))
    active = Column(Boolean)
    public_id = Column(String(200), unique=True)
    position = Column(String(200))


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    description =  Column(String(200))
    public_id = Column(String(200), unique=True)
    cost_assign = Column(Integer)
    cost_completed = Column(Integer)
    is_completed = Column(Boolean)
    worker_id = Column(Integer)
