# In the name of Allah

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from .database_api import get_user_by_password, get_tasks_by_user_id, search_tasks_by_title, delete_task, get_task_by_id
from .database_api import get_completed_tasks_by_user as db_get_all_tasks
from .database_api import get_all_users as db_get_all_users, delete_user as db_delete_user

from pydantic import BaseModel, EmailStr
from typing import Optional
from .database_api import create_user, get_user_by_id, update_user

from .database_api import create_task, update_task, get_task_by_id, search_tasks_by_title

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

class UpdateTaskRequest(BaseModel):
    title: str
    description: str
    completed: bool


def authorize(password: str = Header(...)):
    try:
        res = get_user_by_password(password)

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
async def get_completed_task(authUserID: int = Depends(authorize)):
    try:
        result = db_get_all_tasks(authUserID)

        if result["code"] != 200:
            raise HTTPException(
                status_code=result["code"],
                detail=result["message"]
            )

        if result["message"] is None or len(result["message"]) == 0:
            logger.info(f"No completed tasks found for user {authUserID}")
            return {
                "message": "Not found any task that you want"
            }

        logger.info(f"Completed tasks retrieved successfully for user {authUserID}")

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
def getTasks(title: str | None = None, authUserID: int = Depends(authorize)):
    
    try:
        chosenTasks = []

        if title is None:
            res = get_tasks_by_user_id(authUserID)

            if res['code'] != 200:
                raise HTTPException(
                    status_code=res['code'],
                    detail=res['message']
                )

            chosenTasks = res['message']

        else:
            res = search_tasks_by_title(authUserID, title)

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


@app.delete('/tasks/{task_id}')
def deleteTask(task_id: int, authUserID: int = Depends(authorize)):

    try:
        res = get_task_by_id(task_id)

        if res['code'] != 200:
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )

        task = Task(**res['message'])

        if task.user_id != authUserID:
            raise HTTPException(
                status_code=403,
                detail='Forbidden: not your task'
            )

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

    logger.info(f"Task with ID {task_id} deleted successfully for user {authUserID}")

    return {
        'message': deletedTask
    }


@app.get("/users/")
async def get_all_users(authUserID: int = Depends(authorize)):

    try:
        if authUserID != 1:
            logger.warning(f"Unauthorized access attempt to /users/ by user {authUserID}")
            raise HTTPException(
                status_code=401,
                detail="Not authorized, just super user has access"
            )

        result = db_get_all_users()

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

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, authUserID: int = Depends(authorize)):
    """
    Delete a user by ID.
    Requires authentication (userAuth != -1).
    Validates that user_id is non-negative.
    """

    try:
        if authUserID != 1:
            logger.warning(f"Unauthorized delete attempt by user {authUserID}")
            raise HTTPException(
                status_code=401,
                detail="Not authorized, just super user has access"
            )

        if user_id == 1:
            logger.warning(f"Forbidden delete attempt on super user by user {authUserID}")
            raise HTTPException(
                status_code=403,
                detail="Forbidden: super user can not be deleted"
            )

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
        if authUserID != 1:
            logger.warning(f"Unauthorized create user attempt by user {authUserID}")
            raise HTTPException(
                status_code=401,
                detail="Not authorized, just super user has access"
            )
        
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
        if authUserID != 1:
            logger.warning(f"Unauthorized get user attempt by user {authUserID}")
            raise HTTPException(
                status_code=401,
                detail="Not authorized, just super user has access"
            )

        res = get_user_by_id(user_id)

        if res['code'] != 200:
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )

        user = User(**res['message'])

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
        if authUserID != 1:
            logger.warning(f"Unauthorized update attempt by user {authUserID}")
            raise HTTPException(
                status_code=401,
                detail="Not authorized, just super user has access"
            )

        res = get_user_by_id(user_id)

        if res['code'] != 200:
            raise HTTPException(
                status_code=res['code'],
                detail=res['message']
            )

        existing_user = User(**res['message'])

        update_payload = {}
        if update_data.name is not None:
            update_payload['name'] = update_data.name
        if update_data.email is not None:
            update_payload['email'] = update_data.email
        if update_data.password is not None:
            update_payload['password'] = update_data.password

        res = update_user(user_id, **update_payload)

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

    check = search_tasks_by_title(authUserID, body.title)
    if check['code'] == 200:
        for t in check['message']:
            if t['title'].lower() == body.title.lower():
                raise HTTPException(status_code=409, detail='A task with this title already exists.')

    try:
        res = create_task(body.title, body.description, authUserID)
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
def updateTask(task_id: int, body: UpdateTaskRequest, authUserID: int = Depends(authorize)):
    
    try:
        res = get_task_by_id(task_id)
        if res['code'] != 200:
            raise HTTPException(status_code=res['code'], detail=res['message'])
        task = Task(**res['message'])
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error while retrieving task")
        raise HTTPException(status_code=500, detail="Internal server error")

    if task.user_id != authUserID:
        raise HTTPException(status_code=403, detail='Forbidden: not your task')

    try:
        res = update_task(task_id, body.title, body.description, body.completed, authUserID)
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
        res = get_task_by_id(task_id)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        task = Task(**res['message'])
    except Exception as e:
        logger.exception(f"Unexpected error while getting task\n{e}")
        raise HTTPException(status_code=400, detail="bad request")
    if task.user_id != authUserID:
        raise HTTPException(401, 'Unathorized: not your task')
    return {'message': res['message']}
