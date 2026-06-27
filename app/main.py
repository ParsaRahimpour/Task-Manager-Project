# In the name of Allah

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database_api import get_user_by_email, get_tasks_by_user_id, search_tasks_by_title, delete_task, get_task_by_id

app = FastAPI()

class loginRequest(BaseModel):
    userEmail: str
    password: str


class User(BaseModel):
    user_id: int
    name: str
    email: str
    password: str


class Task(BaseModel):
    task_id: int
    title: str
    description: str
    completed: bool
    user_id: int


userAuth = -1


@app.post('/login')
def login(cred: loginRequest):
    
    global userAuth
    
    if userAuth != -1:
        raise HTTPException(400, 'you are already loged in')
    
    try:    
        res = get_user_by_email(cred.userEmail)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        user = User(**res['message'])

    except Exception as e:
        raise e


    if user.password == cred.password:
        
        userAuth = user.user_id

        return {
            'message': 'successfully loged in'
        }
        
    raise HTTPException(401, 'invalid credentials')



@app.get('/logout')
def logout():

    global userAuth
    
    if userAuth == -1:
        raise HTTPException(400, 'no login to logout')
    
    userAuth = -1

    return {
        'message': 'successful logout'
    }


        
@app.get('/tasks/')
def getTasks(title: str | None = None):
    
    if userAuth == -1:
        raise HTTPException(401, 'not authorized')
    

    chosenTasks = []

    try:
        if title == None:
            res = get_tasks_by_user_id(userAuth)

            if res['code'] != 200:
                raise HTTPException(res['code'], res['message'])
            
            chosenTasks = res['message']

        else:
            res = search_tasks_by_title(userAuth, title)

            if res['code'] != 200:
                raise HTTPException(res['code'], res['message'])
            
            chosenTasks = res['message']

    except Exception as e:
        raise e


    return {
        'message': chosenTasks
    }



@app.delete('/tasks/{task_id}')
def deleteTask(task_id: int):

    if userAuth == -1:
        raise HTTPException(401, 'not authorized')
    

    try:
        res = get_task_by_id(task_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        task = Task(**res['message'])
    
    except Exception as e:
        raise e



    if task.user_id != userAuth:
        raise HTTPException(403, 'Forbidden: not your task')

    try:
        res = delete_task(task_id)

        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        deletedTask = res['message']

    except Exception as e:
        raise e
    
    
    return {
        'message': deletedTask
    }
