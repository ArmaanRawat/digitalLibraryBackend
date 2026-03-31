from fastapi import APIRouter

router = APIRouter()

@router.get("/books/test")
def test_books():
    return {"message": "Books route working"}