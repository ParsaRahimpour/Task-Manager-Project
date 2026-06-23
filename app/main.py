@app.get('/users/')
def get_all_users():
    
    if userAuth == -1:
        raise HTTPException(401, 'not authorized')
    
    users = get_all_users()
    
    if users["code"] != 200:
        raise HTTPException(users["code"], users["message"])
    
    return {
        'users': users["data"]
    }


@app.delete('/users/{user_id}')
def delete_user(user_id: int):
    
    if userAuth == -1:
        raise HTTPException(401, 'not authorized')
    
    result = delete_user(user_id)
    
    if result["code"] != 200:
        raise HTTPException(result["code"], result["message"])
    
    return {
        'message': 'user deleted successfully',
        'user': result["data"]
    }