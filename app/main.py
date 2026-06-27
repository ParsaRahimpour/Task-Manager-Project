from fastapi import FastAPI, HTTPException
from database_api import get_all_users as db_get_all_users, delete_user as db_delete_user

app = FastAPI()

# Global auth variable (will be merged)
userAuth = -1

@app.get('/users/')
def get_all_users():
    global userAuth
    
    if userAuth == -1:
        raise HTTPException(status_code=401, detail='Not authorized')
    
    result = db_get_all_users()
    
    if result["code"] != 200:
        raise HTTPException(status_code=result["code"], detail=result["message"])
    
    return {
        'users': result["message"] if result["message"] else [],
        'count': len(result["message"]) if result["message"] else 0
    }

@app.delete('/users/{user_id}')
def delete_user(user_id: int):
    global userAuth
    
    if userAuth == -1:
        raise HTTPException(status_code=401, detail='Not authorized')
    
    if user_id < 0:
        raise HTTPException(status_code=400, detail='Invalid user ID')
    
    result = db_delete_user(user_id)
    
    if result["code"] != 200:
        raise HTTPException(status_code=result["code"], detail=result["message"])
    
    return {
        'message': 'User deleted successfully',
        'user': result["message"]
    }