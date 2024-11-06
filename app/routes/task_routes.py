from flask import Blueprint, abort, make_response, request, Response 
from app.models.task import Task
from ..db import db
from datetime import datetime

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

# POST
@tasks_bp.post("")
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        response_body = {"details": "Invalid data"}
        return make_response(response_body, 400)
    
    title = request_body["title"]
    description = request_body["description"]
    
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()
    
    response = {"task": new_task.to_dict()}
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
                "is_complete": False
            }
        )
    return tasks_response, 200

# As a client, I want to be able to make a `GET` request to `/tasks/1` when there is at least one saved task and get this response: 200 OK
# review specs for an extra layer
@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)
    response_body = {"task": task.to_dict()}
    return response_body

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()
    response = {
     "task": {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": False
    }
}
    return response, 200

@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    db.session.delete(task)
    db.session.commit()
    response = {
        "details": "Task 1 \"Go on my daily walk 🏞\" successfully deleted"
    }

    return response, 200

# Validation functions
def is_complete(completed_at):
    return False if completed_at is None else True

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        response = {"message": f"Task {task_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"message": f"task {task_id} not found"}
        abort(make_response(response, 404))
    return task