from fastapi import FastAPI , HTTPException
import logging
# Create FastAPI app instance
logger = logging.getLogger(__name__)

app = FastAPI()

#classes
class User:
    id : int
    name : str
    email : str
    
class Task:
    id : int
    title : str
    description : str
    completed : bool
    user_id : int

users = {}
tasks = {}


    
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



@app.get("/tasks/{completed}")
async def get_completed_task(completed : str):
    try:
        result = []
        for task in tasks:
            if task.completed == completed:
                result.append(task)
        if result == None:
            return {"error" : "Not found Any task that you want"}
        return {"success" , result}
    except Exception as e:
            logger.exception(e)
    raise HTTPException(status_code=500, detail="Internal server error")
