import logging
from fastapi import FastAPI, HTTPException
from database_api import get_all_users as db_get_all_users, delete_user as db_delete_user

# ----- Logger setup -----
logger = logging.getLogger(__name__)

# ----- get all users and delete user endpoints -----

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
        raise  # Let FastAPI handle known HTTP errors
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