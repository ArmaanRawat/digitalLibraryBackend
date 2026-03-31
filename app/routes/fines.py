from fastapi import APIRouter

router = APIRouter()

@router.get("/fines/test")
def test_fines():
    return {"message": "Fines route working"}