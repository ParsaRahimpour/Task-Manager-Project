# In the name of Allah

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from .database_api import delete_task, get_users, get_tasks
from .database_api import delete_user as db_delete_user

from pydantic import BaseModel, EmailStr
from typing import Optional
from .database_api import create_user, update_user
from .database_api import create_task, update_task

import logging


logger = logging.getLogger(__name__)
app = FastAPI()


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


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class Task(BaseModel):
    task_id: int
    title: str
    description: str
    completed: bool
    user_id: int

class CreateTaskRequest(BaseModel):
    title: str
    description: str
    user_id: int

class UpdateTaskRequest(BaseModel):
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    user_id: Optional[int] = None


def authorize(password: str = Header(...)):
    try:
        res = get_users(password=password)

        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])

        user = User(**res['message'])

        logger.info("User logged in successfully")
        return user.user_id 

    except Exception as e:
        logger.exception(e)
        raise e


@app.get("/health")
async def get_health():
    try:
        return {"status" : "ok" }
    except Exception as e:
            logger.exception(e)
    raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    try:
        return {"message": "Task Management API"}
    except Exception as e:
        logger.exception(e)
    raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/tasks/completed/")
async def get_completed_task(user_id: int | None = None, authUserID: int = Depends(authorize)):

    try:
        
        result = get_tasks(user_id= user_id, completed=True) 

        if result["code"] != 200:
            raise HTTPException(status_code=result["code"], detail=result["message"])
        
        logger.info(f"user {authUserID} successfully got completed tasks")
        return {"success" , result}
    
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal server error")

        
@app.get('/tasks/')
def getTasks(user_id: int | None = None, title: str | None = None, authUserID: int = Depends(authorize)):
    
    try:

        chosenTasks = []

        if title == None:
            res = get_tasks(user_id= user_id, title= title)

            if res['code'] != 200:
                raise HTTPException(res['code'], res['message'])
            
            chosenTasks = res['message']

    except Exception as e:
        logger.exception(e)
        raise e


    logger.info(f"Tasks retrieved successfully for user {authUserID}")

    return {
        'message': chosenTasks
    }



@app.delete('/tasks/')
def deleteTask(task_id: int, authUserID: int = Depends(authorize)):

    try:

        res = get_tasks(task_id= task_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])

        res = delete_task(task_id)

        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        deletedTask = res['message']


    except Exception as e:
        logger.exception(e)
        raise e
    

    logger.info(f"Task with ID {task_id} deleted successfully by user {authUserID}")
    
    return {
        'message': deletedTask
    }



@app.get("/users/")
async def get_all_users(authUserID: int = Depends(authorize)):

    try:

        result = get_users()
        if result["code"] != 200:
            logger.error(f"get_all_users failed: {result['message']}")
            raise HTTPException(status_code=result["code"], detail=result["message"])

        users = result["message"] if result["message"] else []
        count = len(users)
        logger.info(f"User {authUserID} retrieved all users. Count: {count}")
        return {"users": users, "count": count}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in get_all_users: {e}")
        raise e



@app.delete("/users/")
async def delete_user(user_id: int, authUserID: int = Depends(authorize)):

    try:
        
        if user_id == 1 and user_id != authUserID:
            logger.warning("Forbidden delete attempt")
            raise HTTPException(status_code=403, detail="Forbidden: super user can not be deleted or user delete himself")

        if user_id < 2:
            logger.warning(f"Invalid user_id {user_id} in delete attempt")
            raise HTTPException(status_code=400, detail="Invalid user ID")

        result = db_delete_user(user_id)
        if result["code"] != 200:
            logger.error(f"Delete user failed for id {user_id}: {result['message']}")
            raise HTTPException(status_code=result["code"], detail=result["message"])

        logger.info(f"User {user_id} deleted successfully by user {authUserID}")
        return {"message": "User deleted successfully", "user": result["message"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in delete_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@app.post('/users', status_code=201)
def create_user_endpoint(user: UserCreate, authUserID: int = Depends(authorize)):
    
    try:
        
        res = create_user(name=user.name, email=user.email, password=user.password)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        created_user = User(**res['message'])
        
        logger.info(f'user {authUserID} created a new user with id {created_user.user_id}')
        return {
            'message': created_user
        }
    
    except Exception as e:
        raise e


@app.get('/users/{user_id}')
def get_user_by_id_endpoint(user_id: int, authUserID: int = Depends(authorize)):
    
    try:

        res = get_users(user_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        user = User(**res['message'])
        
        logger.info(f'user {authUserID} retrieved user info with id {user.user_id}')
        return {
            'message': user
        }
    
    except Exception as e:
        raise e


@app.put('/users/{user_id}')
def update_user_endpoint(
    user_id: int,
    update_data: UserUpdate,
    authUserID: int = Depends(authorize)
):
    
    try:

        res = update_user(user_id, **dict(update_data))
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        updated_user = User(**res['message'])
        
        return {
            'message': updated_user
        }
    
    except Exception as e:
        raise e


@app.post('/tasks/')
def createTask(body: CreateTaskRequest, authUserID: int = Depends(authorize)):

    try:
        res = create_task(**body)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        createdTask = res['message']

    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    return {'message': createdTask}



@app.put('/tasks/{task_id}')
def updateTask(body: UpdateTaskRequest, authUserID: int = Depends(authorize)):
    
    try:
        res = update_task(**dict(body))
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        updatedTask = res['message']
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    return {'message': updatedTask}


@app.get('/tasks/{task_id}')
def getTaskById(task_id: int, authUserID: int = Depends(authorize)):
    
    try:
        res = get_tasks(task_id)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    
    return {'message': res['message']}