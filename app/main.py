# In the name of Allah

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database_api import get_user_by_email, get_tasks_by_user_id, search_tasks_by_title, delete_task, get_task_by_id
import logging


logger = logging.getLogger(__name__)
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
    
    try:

        if userAuth != -1:
            raise HTTPException(400, 'you are already loged in')
    
        res = get_user_by_email(cred.userEmail)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        user = User(**res['message'])


        if user.password == cred.password:
            
            userAuth = user.user_id

            logger.info("User logged in successfully")

            return {
                'message': 'successfully loged in'
            }
        
        
        raise HTTPException(401, 'invalid credentials')


    except Exception as e:
        logger.exception(e)
        raise e




@app.get('/logout')
def logout():

    global userAuth
    
    if userAuth == -1:
        logger.error("No user is currently logged in")
        raise HTTPException(400, 'no login to logout')
    
    userAuth = -1

    logger.info("User logged out successfully")

    return {
        'message': 'successful logout'
    }


        
@app.get('/tasks/')
def getTasks(title: str | None = None):
    
    try:

        if userAuth == -1:
            raise HTTPException(401, 'not authorized')
    

        chosenTasks = []

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
        logger.exception(e)
        raise e


    logger.info(f"Tasks retrieved successfully for user")

    return {
        'message': chosenTasks
    }



@app.delete('/tasks/{task_id}')
def deleteTask(task_id: int):

    try:

        if userAuth == -1:
            logger.exception("401: Unauthorized access attempt to delete task")
            raise HTTPException(401, 'not authorized')
        

        res = get_task_by_id(task_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        task = Task(**res['message'])

        if task.user_id != userAuth:
            raise HTTPException(403, 'Forbidden: not your task')

        res = delete_task(task_id)

        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        deletedTask = res['message']


    except Exception as e:
        logger.exception(e)
        raise e
    

    logger.info(f"Task with ID {task_id} deleted successfully for user")
    
    return {
        'message': deletedTask
    }
