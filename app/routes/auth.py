from fastapi import APIRouter, HTTPException
from app.schemas import UserRegister, UserLogin
from app.crud import create_user, get_user_by_email

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_user(user.name, user.email, user.password)
    return {
        "message": "User registered successfully",
        "user": new_user
    }

@router.post("/login")
def login_user(user: UserLogin):
    existing_user = get_user_by_email(user.email)

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    if existing_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "message": "Login successful",
        "user": {
            "id": existing_user["id"],
            "name": existing_user["name"],
            "email": existing_user["email"],
            "role": existing_user["role"]
        }
    }