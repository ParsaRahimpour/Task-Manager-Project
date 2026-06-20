from fastapi import FastAPI
from app.db import engine, Base
from app import models

app = FastAPI()

# creating table
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API with DB is ready"}