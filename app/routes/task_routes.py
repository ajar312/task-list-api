from flask import Blueprint, abort, make_response, request
from app.models.task import Task
from ..db import db
from datetime import datetime
from sqlalchemy import asc, desc
import os
import requests
import json

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

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

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)
    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = db.select(Task).order_by(asc((Task.title)))
    if sort_param == "desc":
        query = db.select(Task).order_by(desc((Task.title))) 

    tasks = db.session.scalars(query)
    tasks_response = []
    for task in tasks:
        tasks_response.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": is_complete(task.completed_at) #--
            }
        )
    return tasks_response, 200

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

@tasks_bp.patch("/<task_id>/mark_complete")
def complete_task(task_id):
    task = validate_task(task_id)
    task.completed_at = datetime.now()
    db.session.commit()
    key = os.environ.get('SLACK_TOKEN')
    url = "https://slack.com/api/chat.postMessage"
    data= {
        "channel": "api-test-channel",
        "text": "My beautiful Task"
    }
    headers = { 
         "Authorization": key
        }
    requests.post(url, data=data, headers=headers)
    
    response = {
        "task": {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": True
    }
}
    return response, 200

@tasks_bp.patch("/<task_id>/mark_incomplete")
def update_not_completed_task(task_id):
    task = validate_task(task_id)
    task.completed_at = None
    db.session.commit()
    response_body = {"task": task.to_dict()}
    return make_response(response_body, 200)


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
