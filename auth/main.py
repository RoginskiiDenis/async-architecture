import hashlib
import json
import os
import uuid

import jwt
from flask import Flask, request
from kafka import KafkaProducer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import User
from lib.enums import ROLE_VALUES

app = Flask("auth")

engine = create_engine(os.environ.get("PG_URL"))

JWT_SECRET = os.environ.get("JWT_SECRET")

def generate_jwt(public_id):
    token = jwt.encode({'public_id': public_id}, JWT_SECRET, algorithm='HS256')
    return token

my_producer = KafkaProducer(
    bootstrap_servers = ['localhost:9092'],
    value_serializer = lambda x: json.dumps(x).encode('utf-8')
    )

@app.route("/signin", methods=["POST", "GET"])
def auth():
    # handle the POST request
    if request.method == 'POST':
        print(request.content_type)
        email = request.form.get('email')
        password = request.form.get('password')

        hash_object = hashlib.sha1(bytes(password, 'utf-8'))
        hashed_client_secret = hash_object.hexdigest()

        with Session(engine) as session:
            rows = session.query(User).filter_by(email=email).all()
            if len(rows) != 1:
                return {"success": False, "message": f"No user with email: {email}"}
            hashed_db_password = rows[0].hashed_password
            user_uuid = rows[0].public_id

        if hashed_client_secret == hashed_db_password:
            token = generate_jwt(user_uuid)
        else:
            return {"success": False, "message": "Invalid password"}
        # otherwise handle the GET request
        return {'success': True,'email': email, "jwt_token": token}
    else:
        # otherwise handle the GET request
        return '''
            <form method="POST">
                <div><label>Email: <input type="text" name="email"></label></div>
                <div><label>Password: <input type="text" name="password"></label></div>
                <input type="submit" value="SignIn">
            </form>'''

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        position = request.form.get('position')
        role = request.form.get('role')
        if role not in ROLE_VALUES:
            return {'success': False, "message": "Invalid role"}

        user_uuid = str(uuid.uuid4())

        hash_object = hashlib.sha1(bytes(password, 'utf-8'))
        hashed_client_secret = hash_object.hexdigest()

        new_user = User(email=email, full_name=name, role=role,
                        active=True, public_id=user_uuid,
                        position=position, hashed_password=hashed_client_secret)

        kafka_event_data = {
            "event_name": "account_created",
            "data":{
                "email": email,
                "full_name": name,
                "role": role,
                "active": True,
                "public_id": user_uuid,
                "position": position,
            }
        }

        token = generate_jwt(user_uuid)
        with Session(engine) as session:
            session.add(new_user)
            session.commit()

        my_producer.send('accounts_stream', value=kafka_event_data)

        return {'success': True, "name": name, 'email': email, "jwt_token": token}

    # otherwise handle the GET request
    return '''
           <form method="POST">
               <div><label>Email: <input type="text" name="email"></label></div>
               <div><label>Password: <input type="text" name="password"></label></div>
               <div><label>Name: <input type="text" name="name"></label></div>
               <div><label>Position: <input type="text" name="position"></label></div>
               <div><label>Role: <input type="text" name="role"></label></div>
               <input type="submit" value="Submit">
           </form>'''

@app.route("/update_user", methods=["POST"])
def update_user():
    # TODO Add update user logic
    return {"success": True}


# run the flask app.
if __name__ == "__main__":
    app.run(debug=True)
