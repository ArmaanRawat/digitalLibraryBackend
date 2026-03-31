from fastapi import APIRouter, HTTPException
from app.crud import get_user_by_id, get_user_fines

router = APIRouter()


@router.get("/fines/{user_id}")
def fines_by_user(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    fines = get_user_fines(user_id)
    return {"fines": fines}
