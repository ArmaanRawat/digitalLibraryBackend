from fastapi import APIRouter

router = APIRouter()

@router.get("/borrow/test")
def test_borrow():
    return {"message": "Borrow route working"}