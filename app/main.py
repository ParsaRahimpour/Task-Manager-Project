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
async def get_completed_task(authUserID: int = Depends(authorize)):
    try:
        result = db_get_all_tasks(authUserID)
        if result["code"] != 200:
            raise HTTPException(status_code=result["code"], detail=result["message"])

        
        if result == None:
            return {"error" : "Not found Any task that you want"}
        
        logger.info("")
        return {"success" , result}
    except Exception as e:
            logger.exception(e)
    raise HTTPException(status_code=500, detail="Internal server error")

        
@app.get('/tasks/')
def getTasks(title: str | None = None, authUserID: int = Depends(authorize)):
    
    try:

        chosenTasks = []

        if title == None:
            res = get_tasks_by_user_id(authUserID)

            if res['code'] != 200:
                raise HTTPException(res['code'], res['message'])
            
            chosenTasks = res['message']

        else:
            res = search_tasks_by_title(authUserID, title)

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
def deleteTask(task_id: int, authUserID: int = Depends(authorize)):

    try:

        res = get_task_by_id(task_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        task = Task(**res['message'])

        if task.user_id != authUserID:
            raise HTTPException(403, 'Forbidden: not your task')

        res = delete_task(task_id)

        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        deletedTask = res['message']


    except Exception as e:
        logger.exception(e)
        raise e
    

    logger.info(f"Task with ID {task_id} deleted successfully for user {authUserID}")
    
    return {
        'message': deletedTask
    }



@app.get("/users/")
async def get_all_users(authUserID: int = Depends(authorize)):

    try:
        # Removed: authUserID != 1 check

        result = db_get_all_users()
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
        raise HTTPException(status_code=500, detail="Internal server error")  # Changed: was raise e



@app.delete("/users/{user_id}")
async def delete_user(user_id: int, authUserID: int = Depends(authorize)):
    """
    Delete a user by ID.
    Requires authentication (userAuth != -1).
    Validates that user_id is non-negative.
    """
    
    try:
        # Removed: authUserID != 1 check

        # Changed: self-deletion prevention
        if user_id == authUserID:
            logger.warning("Forbidden delete attempt")
            raise HTTPException(status_code=403, detail="Cannot delete your own account")

        # Changed: invalid user_id check
        if user_id < 1:
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
        if authUserID != 1:
            logger.warning("Unauthorized delete attempt")
            raise HTTPException(status_code=401, detail="Not authorized, just super user has access")
        
        res = create_user(name=user.name, email=user.email, password=user.password)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        created_user = User(**res['message'])
        
        return {
            'message': created_user
        }
    
    except Exception as e:
        raise e


@app.get('/users/{user_id}')
def get_user_by_id_endpoint(user_id: int, authUserID: int = Depends(authorize)):
    
    try:
        if authUserID != 1:
            logger.warning("Unauthorized delete attempt")
            raise HTTPException(status_code=401, detail="Not authorized, just super user has access")

        res = get_user_by_id(user_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        user = User(**res['message'])
        
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
        if authUserID != 1:
            logger.warning("Unauthorized delete attempt")
            raise HTTPException(status_code=401, detail="Not authorized, just super user has access")
        
        res = get_user_by_id(user_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
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
            raise HTTPException(res['code'], res['message'])
        
        updated_user = User(**res['message'])
        
        return {
            'message': updated_user
        }
    
    except Exception as e:
        raise e


@app.post('/tasks/')
def createTask(body: CreateTaskRequest, authUserID: int = Depends(authorize)):

    check = search_tasks_by_title(authUserID, body.title)
    if check['code'] == 200:
        for t in check['message']:
            if t['title'].lower() == body.title.lower():
                raise HTTPException(409, 'A task with this title already exists.')

    try:
        res = create_task(body.title, body.description, authUserID)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        createdTask = res['message']

    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    return {'message': createdTask}



@app.put('/tasks/{task_id}')
def updateTask(task_id: int, body: UpdateTaskRequest, authUserID: int = Depends(authorize)):
    
    try:
        res = get_task_by_id(task_id)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        task = Task(**res['message'])
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    if task.user_id != authUserID:
        raise HTTPException(403, 'Forbidden: not your task')
    try:
        res = update_task(task_id, body.title, body.description, body.completed, authUserID)
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
        res = get_task_by_id(task_id)
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        task = Task(**res['message'])
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'internal server error')
    if task.user_id != authUserID:
        raise HTTPException(401, 'Unathorized: not your task')
    return {'message': res['message']}