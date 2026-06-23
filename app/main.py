from fastapi import FastAPI, HTTPException, Query, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="Task Management API")

# ====================== Global State ======================
userAuth = -1
tasks = []
task_id_counter = 1

# ====================== Schemas ======================
class LoginRequest(BaseModel):
    userID: int
    password: str

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

# ====================== Auth Helpers ======================
def get_current_user():
    if userAuth == -1:
        raise HTTPException(status_code=401, detail="Not authorized")
    return userAuth

def check_task_ownership(task: dict, user_id: int):
    if task["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: not your task")

# ====================== Auth Endpoints ======================
@app.post("/login")
async def login(cred: LoginRequest):
    global userAuth
    if userAuth != -1:
        raise HTTPException(status_code=400, detail="You are already logged in")
    
    users = [
        {"userID": 0, "password": "ali"},
        {"userID": 1, "password": "gholi"},
        {"userID": 2, "password": "maria"},
    ]
    
    for user in users:
        if user["userID"] == cred.userID and user["password"] == cred.password:
            userAuth = user["userID"]
            return {"message": "Successfully logged in"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/logout")
async def logout():
    global userAuth
    if userAuth == -1:
        raise HTTPException(status_code=400, detail="No login to logout")
    userAuth = -1
    return {"message": "Successful logout"}


# ====================== Root & Health ======================
@app.get("/")
async def root():
    return {"message": "Task Management API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# ====================== Tasks Endpoints ======================

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskBase, current_user: int = Depends(get_current_user)):
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
async def get_task_by_id(task_id: int, current_user: int = Depends(get_current_user)):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    current_user: int = Depends(get_current_user)
):
    for task in tasks:
        if task["id"] == task_id:
            check_task_ownership(task, current_user)  
            
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
    completed: Optional[bool] = Query(None),
    title: Optional[str] = Query(None),
    current_user: int = Depends(get_current_user)
):
    filtered = [t for t in tasks if t["user_id"] == current_user]  

    if completed is not None:
        filtered = [t for t in filtered if t["completed"] == completed]
    if title:
        filtered = [t for t in filtered if title.lower() in t["title"].lower()]

    return filtered


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, current_user: int = Depends(get_current_user)):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            check_task_ownership(task, current_user)
            deleted = tasks.pop(index)
            return {"message": "Task deleted successfully", "task": deleted}
    raise HTTPException(status_code=404, detail="Task not found")
