from fastapi import APIRouter

router = APIRouter()

@router.get("/users/test")
def test_users():
    return {"message": "Users route working"}