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

    if title is None or description is None:
        bad_request = {
            "details": "Invalid data"
        }
        return bad_request, 400

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
                "is_complete": is_complete(task.completed_at)
            }
        )
    return tasks_response, 200

# As a client, I want to be able to make a `GET` request to `/tasks/1` when there is at least one saved task and get this response: 200 OK

@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)
    response = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": is_complete(task.completed_at)
    }
    return response, 200




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
        "title": task.title ,
        "description": task.description ,
        "is_complete": is_complete(task.completed_at)
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
        response = {"message": f"task {task_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response = {"message": f"task {task_id} not found"}
        abort(make_response(response, 404))
    return task, 200