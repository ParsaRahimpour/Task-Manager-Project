from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr
from typing import Optional

# database module
from database import create_user, get_user_by_id, update_user

app = FastAPI()

# ---------- Models ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

# ---------- Authentication (Error 401) ----------
VALID_API_KEY = "secret-key-123"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user_id(api_key: Optional[str] = Security(api_key_header)) -> int:
    if api_key is None or api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    # Here the valid key belongs to user with id=1
    return 1

# ---------- 1. Create User ----------
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user_endpoint(user: UserCreate):
    try:
        result = create_user(name=user.name, email=user.email)
        return UserResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------- 2. Get User by ID ----------
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id_endpoint(user_id: int):
    try:
        result = get_user_by_id(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------- 3. Update User (with Error 401) ----------
@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    update_data: UserUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    # Check authorization (401)
    if current_user_id != user_id:
        raise HTTPException(status_code=401, detail="Not authorized to update this user")

    try:
        # Check if user exists
        existing = get_user_by_id(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        # Update
        updated = update_user(
            user_id,
            name=update_data.name,
            email=update_data.email
        )
        return UserResponse(**updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))