from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from database_api import create_user, get_user_by_id, update_user, get_user_by_email

app = FastAPI()

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

class loginRequest(BaseModel):
    userEmail: str
    password: str

userAuth = -1

@app.post('/login')
def login(cred: loginRequest):
    global userAuth
    
    if userAuth != -1:
        raise HTTPException(400, 'you are already logged in')
    
    try:
        res = get_user_by_email(cred.userEmail)
        
        if res['code'] != 200:
            raise HTTPException(res['code'], res['message'])
        
        user = UserResponse(**res['message'])
    
    except Exception as e:
        raise e
    
    if user.password == cred.password:
        userAuth = user.id
        return {
            'message': 'successfully logged in'
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
