import json
import os
import random
import threading
import uuid

import jwt
from flask import Flask, request
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Task, User
from lib.enums import Role
from lib.db_utlis import get_all_workers

app = Flask(__name__)

engine = create_engine(os.environ.get("PG_URL"))
JWT_SECRET = os.environ.get("JWT_SECRET")

my_consumer = KafkaConsumer(
    'accounts_stream',
     bootstrap_servers = ['localhost : 9092'],
     auto_offset_reset = 'earliest',
     enable_auto_commit = True,
     group_id = 'my-group',
     value_deserializer = lambda x : json.loads(x.decode('utf-8'))
)

my_producer = KafkaProducer(
    bootstrap_servers = ['localhost:9092'],
    value_serializer = lambda x: json.dumps(x).encode('utf-8')
)

def start_listening():
    print("Started kafka consumer listening")
    for message in my_consumer:
        message = message.value
        data = message['data']
        new_user = User(email=data['email'], full_name=data['full_name'], role=data['role'],
                        active=data['active'], public_id=data['public_id'],
                        position=data['position'])
        with Session(engine) as session:
            session.add(new_user)
            session.commit()

def get_user_id_from_request(request):
    authorization_header = request.headers.get('authorization')
    token = authorization_header.replace("Bearer ","")
    decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    public_id = decoded['public_id']

    with Session(engine) as session:
        rows = session.query(User).filter_by(public_id=public_id).all()
        user_id = rows[0].id

    return user_id

def get_user_role_from_request(request) -> Role:
    authorization_header = request.headers.get('authorization')
    token = authorization_header.replace("Bearer ","")
    decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    public_id = decoded['public_id']

    with Session(engine) as session:
        rows = session.query(User).filter_by(public_id=public_id).all()
        user_role = Role(rows[0].role)

    return user_role

@app.route("/shuffle", methods=["POST", "GET"])
def shuffle():
    role = get_user_role_from_request(request)
    if role not in (Role.ADMIN, Role.MANAGER):
        return {'success': False, "message": "Not authorized"}

    all_users = get_all_workers(engine)
    with Session(engine) as session:
        tasks = session.query(Task).filter_by(is_completed=False).all()
        for task in tasks:
            user_public_id, user_id = random.choice(all_users)
            task.worker_id = user_id

            kafka_event_data = {
                "event_name": "task_assigned_by_shuffle",
                "data":{
                    "user_public_id": user_public_id,
                    "task_public_id": task.public_id
                }
            }
            my_producer.send('tasks', value=kafka_event_data)

        session.commit()

    return {'success': True}

@app.route("/close_task", methods=["POST"])
def close_task():
    user_id = get_user_id_from_request(request)
    task_id = request.json.get('task_public_id')

    with Session(engine) as session:
        task = session.query(Task).filter_by(public_id=task_id).first()
        if task.worker_id != user_id:
            return {'success': False}

        kafka_event_data = {
                "event_name": "task_completed",
                "data":{
                    "task_public_id": task.public_id
                }
            }
        my_producer.send('tasks', value=kafka_event_data)
        
        task.is_completed = True
        session.commit()

    return {'success': True}

@app.route("/list_tasks", methods=["GET"])
def list_tasks():
    user_id = get_user_id_from_request(request)
    with Session(engine) as session:
        tasks = session.query(Task).filter_by(worker_id=user_id).filter_by(is_completed=False).all()
        task_list = [{'description': task.description, 'public_id': task.public_id} for task in tasks]

    return {'success': True, "tasks": task_list}

@app.route("/create_task", methods=["POST", "GET"])
def create_task():
    # handle the POST request
    if request.method == 'POST':
        description = request.form.get('description')
        
        possible_workers = get_all_workers(engine)

        worker_public_id, worker_id = random.choice(possible_workers)
        if len(possible_workers) == 0:
            return {'success': False, "message": "No workers in the system"}

        task_uuid = str(uuid.uuid4())
        cost_assign = random.randint(-20, -10)
        cost_completed = random.randint(20, 40)
        new_task = Task(description=description,
                        is_completed=False, public_id=task_uuid,
                        cost_assign=cost_assign, cost_completed=cost_completed,
                        worker_id=worker_id)
        task_id = new_task.public_id
        with Session(engine) as session:
            session.add(new_task)
            session.commit()
        
        kafka_event_data = {
            "event_name": "task_created",
            "data":{
                "description": description,
                "public_id": task_uuid,
                "cost_assign": cost_assign,
                "cost_completed": cost_completed,
                "worker_public_id": worker_public_id
            }
        }
        my_producer.send('tasks_stream', value=kafka_event_data)

        return {'success': True, 'task_id': task_id, 'assignee': worker_public_id}

    # otherwise handle the GET request
    return '''
           <form method="POST">
               <div><label>Description: <input type="text" name="description"></label></div>
               <input type="submit" value="Create">
           </form>'''

@app.route("/update_task", methods=["POST"])
def update_task():
    # TODO Add update task logic
    return {"success": True}


# run the flask app.
if __name__ == "__main__":
    x = threading.Thread(target=start_listening)
    x.start()
    app.run(debug=True, port=5001)
