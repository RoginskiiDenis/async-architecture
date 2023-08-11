import hashlib
import json
import jwt
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import User
import uuid

from flask import Flask, request

app = Flask(__name__)

engine = create_engine(os.environ.get("PG_URL"))

JWT_SECRET = os.environ.get("JWT_SECRET")

def generate_jwt(email):
    token = jwt.encode({'email': email}, JWT_SECRET, algorithm='HS256')
    return token


# API Route for checking the client_id and client_secret
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
            print(len(rows))
            if len(rows) != 1:
                return {"success": False}
            hashed_db_password = rows[0].hashed_password

        if hashed_client_secret == hashed_db_password:
            token = generate_jwt(email)
        else:
            return {"success": False}
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
    # handle the POST request
    if request.method == 'POST':
        print(request.content_type)
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        position = request.form.get('position')
        role = request.form.get('role')
        user_uuid = str(uuid.uuid4())

        hash_object = hashlib.sha1(bytes(password, 'utf-8'))
        hashed_client_secret = hash_object.hexdigest()

        new_user = User(email=email, full_name=name,role=role, 
                        active=True, public_id=user_uuid,
                        position=position, hashed_password=hashed_client_secret)

        token = generate_jwt(email)
        with Session(engine) as session:
            session.add(new_user)
            session.commit()

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


# run the flask app.
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)