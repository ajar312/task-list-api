from flask import Blueprint, abort, make_response, request 
from app.models.task import Task
from ..db import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")
# POST
@tasks_bp.post("")
def create_task():
    request_body = request.get_json()
    title = request_body["title"]
    description = request_body["description"]
    completed_at = request_body["completed_at"]

    new_task = Task(title=title, description=description,completed_at=completed_at)
    db.session.add(new_task)
    db.session.commit()

    response = {
        "task": {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": new_task.completed_at
        }
    }
    return response, 201

# GET 
# 1. As a client, I want to be able to make a `GET` request to `/tasks` when there is at least one saved task 

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task).order_by(Task.id)
    tasks = db.session.scalars(query)
    tasks_response = []
    for task in tasks:
        tasks_response.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at is None else True 
            }
        )
    return tasks_response, 200

# 2. As a client, I want to be able to make a `GET` request to `/tasks` when there are zero saved tasks

