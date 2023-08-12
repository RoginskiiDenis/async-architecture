import hashlib
import json
import jwt
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models import User, Task
import uuid
import random

from flask import Flask, request

app = Flask(__name__)

engine = create_engine(os.environ.get("PG_URL"))
JWT_SECRET = os.environ.get("JWT_SECRET")

WORKER_ROLE = "worker"
MANAGER_ROLE = "manager"
ADMIN_ROLE = "admin"

def get_user_id_from_request(request):
    authorizationHeader = request.headers.get('authorization')	
    token = authorizationHeader.replace("Bearer ","")
    print(authorizationHeader)
    decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    email = decoded['email']

    with Session(engine) as session:
        rows = session.query(User).filter_by(email=email).all()        
        user_id = rows[0].id

    return user_id


@app.route("/shuffle", methods=["POST", "GET"])
def shuffle():
    return {'success':True}


@app.route("/close_task", methods=["POST"])
def close_task():
    user_id = get_user_id_from_request(request)
    task_id = request.json.get('task_public_id')

    with Session(engine) as session:
        task = session.query(Task).filter_by(public_id=task_id).first()
        print(task.worker_id)
        print(user_id)
        if task.worker_id != user_id:
            return {'success': False}
        else:
            task.is_completed = True
            session.commit()

    return {'success': True}


@app.route("/create_task", methods=["POST", "GET"])
def create_task():
    # handle the POST request
    if request.method == 'POST':
        description = request.form.get('description')
        possible_workers = []
        with Session(engine) as session:
            rows = session.query(User).filter_by(role=WORKER_ROLE).all()
            for r in rows:
                possible_workers.append(r.id)

        if len(possible_workers) == 0:
            return {'success': False, "message": "No workers in the system"}

        new_task = Task(description=description, 
                        is_completed=False, public_id=str(uuid.uuid4()),
                        cost_assign=random.randint(-20, -10), cost_completed=random.randint(20, 40),
                        worker_id=random.choice(possible_workers))
        task_id = new_task.public_id
        worker_id = new_task.worker_id
        with Session(engine) as session:
            session.add(new_task)
            session.commit()

        return {'success': True, 'task_id': task_id, 'assignee': worker_id}

    # otherwise handle the GET request
    return '''
           <form method="POST">
               <div><label>Description: <input type="text" name="description"></label></div>
               <input type="submit" value="Create">
           </form>'''


# run the flask app.
if __name__ == "__main__":
    app.run(debug=True, port=5001)