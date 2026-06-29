# In the name of Allah

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database_api import get_user_by_email, get_tasks_by_user_id, search_tasks_by_title, delete_task, get_task_by_id
from database_api import get_completed_tasks_by_user as db_get_all_tasks
from database_api import get_all_users as db_get_all_users, delete_user as db_delete_user

from pydantic import BaseModel, EmailStr
from typing import Optional
from database_api import create_user, get_user_by_id, update_user, get_user_by_email

from database_api import create_task, update_task, get_task_by_id, get_tasks_by_user_id

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


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str


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

userAuth = -1


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



@app.get("/tasks/completed/{id}")
async def get_completed_task(id : int):
    try:
        if userAuth == -1:
            raise HTTPException(401, 'not authorized')
        result = db_get_all_tasks(id)
        if result["code"] != 200:
            raise HTTPException(status_code=result["code"], detail=result["message"])

        
        if result == None:
            return {"error" : "Not found Any task that you want"}
        return {"success" , result}
    except Exception as e:
            logger.exception(e)
    raise HTTPException(status_code=500, detail="Internal server error")



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

  
  

@app.get("/users/")
async def get_all_users():
    """
    Retrieve all users.
    Requires authentication (userAuth != -1).
    """
    global userAuth
    try:
        if userAuth == -1:
            logger.warning("Unauthorized access attempt to /users/")
            raise HTTPException(status_code=401, detail="Not authorized")

        result = db_get_all_users()
        if result["code"] != 200:
            logger.error(f"get_all_users failed: {result['message']}")
            raise HTTPException(status_code=result["code"], detail=result["message"])

        users = result["message"] if result["message"] else []
        count = len(users)
        logger.info(f"User {userAuth} retrieved all users. Count: {count}")
        return {"users": users, "count": count}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in get_all_users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """
    Delete a user by ID.
    Requires authentication (userAuth != -1).
    Validates that user_id is non-negative.
    """
    global userAuth
    try:
        if userAuth == -1:
            logger.warning("Unauthorized delete attempt")
            raise HTTPException(status_code=401, detail="Not authorized")

        if user_id < 0:
            logger.warning(f"Invalid user_id {user_id} in delete attempt")
            raise HTTPException(status_code=400, detail="Invalid user ID")

        result = db_delete_user(user_id)
        if result["code"] != 200:
            logger.error(f"Delete user failed for id {user_id}: {result['message']}")
            raise HTTPException(status_code=result["code"], detail=result["message"])

        logger.info(f"User {user_id} deleted successfully by user {userAuth}")
        return {"message": "User deleted successfully", "user": result["message"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in delete_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post('/users', status_code=201)
def create_user_endpoint(user: UserCreate):
    try:
        res = create_user(name=user.name, email=user.email, password=user.password)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        created_user = UserResponse(**res['message'])
        
        return {
            'message': created_user
        }
    
    except Exception as e:
        raise e

@app.get('/users/{user_id}')
def get_user_by_id_endpoint(user_id: int):
    try:
        res = get_user_by_id(user_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        user = UserResponse(**res['message'])
        
        return {
            'message': user
        }
    
    except Exception as e:
        raise e

@app.put('/users/{user_id}')
def update_user_endpoint(
    user_id: int,
    update_data: UserUpdate
):
    global userAuth
    
    if userAuth == -1:
        raise HTTPException(401, 'not authorized')
    
    try:
        res = get_user_by_id(user_id)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        existing_user = UserResponse(**res['message'])
        
        if userAuth != user_id:
            raise HTTPException(401, 'Not authorized to update this user')
        
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
        
        updated_user = UserResponse(**res['message'])
        
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
        res = update_task(**body)
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
