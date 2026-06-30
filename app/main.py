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
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )

        user = User(**res['message'])

        logger.info(f"User {user.user_id} logged in successfully")
        return user.user_id

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during authorization {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/health")
async def get_health():
    try:
        return {
            "status": "ok"
        }

    except Exception as e:
        logger.exception(f"Unexpected error during health check {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/")
async def root():
    try:
        return {
            "message": "Task Management API"
        }

    except Exception as e:
        logger.exception(f"Unexpected error in root endpoint, {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get("/tasks/completed/")
async def get_completed_task(user_id: int | None = None, authUserID: int = Depends(authorize)):

    try:
        
        result = get_tasks(user_id= user_id, completed=True) 

        if result["code"] != 200:
            raise HTTPException(status_code=result["code"], detail=result["message"])
        
        if result["message"] is None or len(result["message"]) == 0:
            logger.info(f"No completed tasks found")
            return {
                "message": "Not found any task that you want"
            }

        logger.info(f"user {authUserID} successfully got completed tasks")
        return {
            "success": True,
            "tasks": result["message"]
        }
    
    except HTTPException:
        raise
    except Exception  as e:
        logger.exception(f"Unexpected error while retrieving completed tasks for user {authUserID} \n {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
        

        

        


        

    

        
@app.get('/tasks/')
def getTasks(user_id: int | None = None, title: str | None = None, authUserID: int = Depends(authorize)):
    
    try:
        chosenTasks = []

        if title == None:
            res = get_tasks(user_id= user_id, title= title)
        

            if res['code'] != 200:
                raise HTTPException(
                    status_code=res['code'],
                    detail=res['message']
                )

            chosenTasks = res['message']

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while retrieving tasks for user {authUserID}\n{e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

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
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )

        deletedTask = res['message']

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while deleting task {task_id}\n{e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    logger.info(f"Task with ID {task_id} deleted successfully by user {authUserID}")
    

    return {
        'message': deletedTask
    }


@app.get("/users/")
async def get_all_users(authUserID: int = Depends(authorize)):

    try:

        result = get_users()

        if result["code"] != 200:
            raise HTTPException(
                status_code=result["code"],
                detail=result["message"]
            )

        users = result["message"] if result["message"] else []
        count = len(users)

        logger.info(f"User {authUserID} retrieved all users. Count: {count}")

        return {
            "users": users,
            "count": count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while retrieving all users\n{e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.delete("/users/")
async def delete_user(user_id: int, authUserID: int = Depends(authorize)):

    try:
        
        if user_id == 1 and user_id != authUserID:
            logger.warning("Forbidden delete attempt")
            raise HTTPException(status_code=403, detail="Forbidden: super user can not be deleted or user delete himself")


        if user_id < 2:
            logger.warning(f"Invalid user_id {user_id} in delete attempt")
            raise HTTPException(
                status_code=400,
                detail="Invalid user ID"
            )

        result = db_delete_user(user_id)

        if result["code"] != 200:
            raise HTTPException(
                status_code=result["code"],
                detail=result["message"]
            )

        logger.info(f"User {user_id} deleted successfully by user {authUserID}")

        return {
            "message": "User deleted successfully",
            "user": result["message"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while deleting user {user_id}\n{e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.post('/users', status_code=201)
def create_user_endpoint(user: UserCreate, authUserID: int = Depends(authorize)):
    
    try:

        
        res = create_user(
            name=user.name,
            email=user.email,
            password=user.password
        )
        
        if res['code'] != 200:
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )
        
        created_user = User(**res['message'])
        
        logger.info(f'user {authUserID} created a new user with id {created_user.user_id}')
        return {
            'message': created_user
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while creating user\n{e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.get('/users/{user_id}')
def get_user_by_id_endpoint(user_id: int, authUserID: int = Depends(authorize)):
    
    try:

        res = get_users(user_id)
        

        if res['code'] != 200:
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )

        user = User(**res['message'])
        
        logger.info(f'user {authUserID} retrieved user info with id {user.user_id}')

        return {
            'message': user
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while retrieving user {user_id}\n{e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.put('/users/{user_id}')
def update_user_endpoint(
    user_id: int,
    update_data: UserUpdate,
    authUserID: int = Depends(authorize)
):
    
    try:

        res = update_user(user_id, **dict(update_data))
        


        if res['code'] != 200:
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )

        updated_user = User(**res['message'])

        return {
            'message': updated_user
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while updating user {user_id}\n{e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@app.post('/tasks/')
def createTask(body: CreateTaskRequest, authUserID: int = Depends(authorize)):


    try:
        res = create_task(**body)
        if res['code'] != 200:
            raise HTTPException(status_code=res['code'], detail=res['message'])
        createdTask = res['message']

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while creating task\n{e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    return {'message': createdTask}



@app.put('/tasks/{task_id}')
def updateTask(body: UpdateTaskRequest, authUserID: int = Depends(authorize)):
    
    try:
        res = update_task(**dict(body))

        if res['code'] != 200:
            raise HTTPException(status_code=res['code'], detail=res['message'])
        updatedTask = res['message']
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error while updating task\n{e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {'message': updatedTask}


@app.get('/tasks/{task_id}')
def getTaskById(task_id: int, authUserID: int = Depends(authorize)):
    
    try:
        res = get_tasks(task_id)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])


    except Exception as e:
        logger.exception(f"Unexpected error while getting task\n{e}")
        raise HTTPException(status_code=400, detail="bad request")
    return {'message': res['message']}
