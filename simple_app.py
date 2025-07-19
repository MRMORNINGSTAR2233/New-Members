from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from typing import Dict, List, Optional

app = FastAPI()

# Sample data
messages = []
tasks = []

# Models
class Message(BaseModel):
    content: str
    sender: str

class Task(BaseModel):
    title: str
    description: str
    completed: bool = False

# Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request {request.method} {request.url.path}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Messages API
@app.get("/messages")
async def get_messages():
    return messages

@app.post("/messages")
async def create_message(message: Message):
    messages.append(message.dict())
    return {"id": len(messages), "status": "message created"}

# Tasks API
@app.get("/tasks")
async def get_tasks(completed: Optional[bool] = None):
    if completed is None:
        return tasks
    return [task for task in tasks if task["completed"] == completed]

@app.post("/tasks")
async def create_task(task: Task):
    tasks.append(task.dict())
    return {"id": len(tasks), "status": "task created"}

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: Task):
    if task_id < 1 or task_id > len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id-1] = task.dict()
    return {"status": "task updated"}
