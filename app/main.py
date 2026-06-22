# In the name of Allah

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class loginRequest(BaseModel):
    userID: int
    password: str


userAuth = -1

tasks = [
    {
        'title': 'docker',
        'userID': 1,
        'taskID': 0
    },
    {
        'title': 'git',
        'userID': 0,
        'taskID': 1
    },
    {
        'title': 'docker-git',
        'userID': 0,
        'taskID': 2
    },
    {
        'title': 'ubuntu',
        'userID': 2,
        'taskID': 3
    }
]

users = [
    {
        'userID': 0,
        'password': 'ali'
    },
    {
        'userID': 1,
        'password': 'gholi'
    },
    {
        'userID': 2,
        'password': 'maria'
    },
]


@app.post('/login')
def login(cred: loginRequest):
    
    global userAuth
    
    if userAuth != -1:
        raise HTTPException(400, 'you are already loged in')
    
    for user in users:
        if user['userID'] == cred.userID and user['password'] == cred.password:
        
            userAuth = user['userID']

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

    for task in tasks:
        if task['userID'] == userAuth:
            if title == None or title.lower() in task['title'].lower():
                chosenTasks.append(task)
    
    return {
        'message': chosenTasks
    }
