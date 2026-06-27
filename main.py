from fastapi import FastAPI , HTTPException
import logging
from database_api import get_completed_tasks_by_user as db_get_completed_tasks_by_user
# Create FastAPI app instance
logger = logging.getLogger(__name__)

app = FastAPI()


    
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
        result = get_all_tasks(id)
        if result["code"] != 200:
            raise HTTPException(status_code=result["code"], detail=result["message"])

        
        if result == None:
            return {"error" : "Not found Any task that you want"}
        return {"success" , result}
    except Exception as e:
            logger.exception(e)
    raise HTTPException(status_code=500, detail="Internal server error")
