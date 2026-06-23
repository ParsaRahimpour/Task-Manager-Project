from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="Task Management API")

# ====================== In-Memory Storage ======================
tasks = []
task_id_counter = 1

# ====================== Schemas ======================
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    completed: bool = False
    user_id: int = Field(..., gt=0)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    user_id: Optional[int] = Field(None, gt=0)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    user_id: int

# ====================== Root & Health ======================
@app.get("/")
async def root():
    return {"message": "Task Management API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# ====================== Tasks Endpoints ======================

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskBase):
    """Create a new task"""
    global task_id_counter
    
    new_task = {
        "id": task_id_counter,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "user_id": task.user_id
    }
    tasks.append(new_task)
    task_id_counter += 1
    return new_task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int):
    """Get task by ID"""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update task"""
    for task in tasks:
        if task["id"] == task_id:
            if task_update.title is not None:
                task["title"] = task_update.title
            if task_update.description is not None:
                task["description"] = task_update.description
            if task_update.completed is not None:
                task["completed"] = task_update.completed
            if task_update.user_id is not None:
                task["user_id"] = task_update.user_id
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/tasks", response_model=List[TaskResponse])
async def get_all_tasks(
    completed: Optional[bool] = Query(None, description="Filter completed tasks"),
    title: Optional[str] = Query(None, description="Search by title")
):
    """Get all tasks with optional filtering"""
    filtered_tasks = tasks.copy()

    if completed is not None:
        filtered_tasks = [t for t in filtered_tasks if t["completed"] == completed]

    if title:
        filtered_tasks = [t for t in filtered_tasks if title.lower() in t["title"].lower()]

    return filtered_tasks


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete task"""
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            deleted_task = tasks.pop(index)
            return {
                "message": "Task deleted successfully",
                "task": deleted_task
            }
    raise HTTPException(status_code=404, detail="Task not found")
