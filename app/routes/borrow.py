from fastapi import APIRouter, HTTPException
from app.schemas import BorrowRequest, ReturnRequest
from app.crud import borrow_book, return_book, get_borrow_history, get_user_by_id

router = APIRouter()


@router.post("/borrow/{book_id}")
def borrow_book_route(book_id: int, request: BorrowRequest):
    borrowed_book, error = borrow_book(request.user_id, book_id)

    if error == "user_not_found":
        raise HTTPException(status_code=404, detail="User not found")
    if error == "book_not_found":
        raise HTTPException(status_code=404, detail="Book not found")
    if error == "no_copies_available":
        raise HTTPException(status_code=400, detail="No copies available")
    if error == "already_borrowed":
        raise HTTPException(status_code=400, detail="Book already borrowed by this user")

    return {
        "message": "Book borrowed successfully",
        "borrow_record": borrowed_book
    }


@router.post("/return/{book_id}")
def return_book_route(book_id: int, request: ReturnRequest):
    returned_book, error = return_book(request.user_id, book_id)

    if error == "user_not_found":
        raise HTTPException(status_code=404, detail="User not found")
    if error == "book_not_found":
        raise HTTPException(status_code=404, detail="Book not found")
    if error == "active_borrow_not_found":
        raise HTTPException(status_code=404, detail="No active borrow record found")

    return {
        "message": "Book returned successfully",
        "return_record": returned_book
    }


@router.get("/borrow/history/{user_id}")
def borrow_history(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = get_borrow_history(user_id)
    return {"history": history}
