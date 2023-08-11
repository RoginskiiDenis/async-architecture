import hashlib
import json
import jwt
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import User
import uuid
from sqlalchemy.sql import text

engine = create_engine(os.environ.get("PG_URL"))
with Session(engine) as session:
    res = session.execute(text("SELECT * FROM users_tracker"))
    print(res.all())

with Session(engine) as session:
    rows = session.query(User).filter_by(email="katya@gmail.com").all()
    print(rows[0].hashed_password)

JWT_SECRET = os.environ.get("JWT_SECRET")
def generate_jwt(email):
    token = jwt.encode({'email': email}, JWT_SECRET, algorithm='HS256')
    return token
print(generate_jwt('dddd'))