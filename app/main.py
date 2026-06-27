from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database_api import create_task, update_task, get_task_by_id, search_tasks_by_title

app = FastAPI()

class Task(BaseModel):
    task_id: int
    title: str
    description: str
    completed: bool
    user_id: int

class CreateTaskRequest(BaseModel):
    title: str
    description: str

class UpdateTaskRequest(BaseModel):
    title: str
    description: str
    completed: bool

userAuth = -1


@app.post('/tasks/')
def createTask(body: CreateTaskRequest):
    if userAuth == -1:
        raise HTTPException(401, 'not authorized')

    check = search_tasks_by_title(userAuth, body.title)
    if check['code'] == 200:
        for t in check['message']:
            if t['title'].lower() == body.title.lower():
                raise HTTPException(409, 'A task with this title already exists.')

    try:
        res = create_task(body.title, body.description, userAuth)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        createdTask = res['message']
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    return {'message': createdTask}


@app.put('/tasks/{task_id}')
def updateTask(task_id: int, body: UpdateTaskRequest):
    if userAuth == -1:
        raise HTTPException(401, 'not authorized')
    try:
        res = get_task_by_id(task_id)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        task = Task(**res['message'])
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    if task.user_id != userAuth:
        raise HTTPException(403, 'Forbidden: not your task')
    try:
        res = update_task(task_id, body.title, body.description, body.completed, userAuth)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        updatedTask = res['message']
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    return {'message': updatedTask}


@app.get('/tasks/{task_id}')
def getTaskById(task_id: int):
    if userAuth == -1:
        raise HTTPException(401, 'not authorized')
    try:
        res = get_task_by_id(task_id)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        task = Task(**res['message'])
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    if task.user_id != userAuth:
        raise HTTPException(403, 'Forbidden: not your task')
    return {'message': res['message']}
