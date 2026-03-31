from fastapi import APIRouter, HTTPException, Query
from app.schemas import BookCreate
from app.crud import create_book, get_all_books, search_books, get_overdue_books

router = APIRouter()


@router.post("/books")
def add_book(book: BookCreate):
    new_book = create_book(
        title=book.title,
        author=book.author,
        category=book.category,
        total_copies=book.total_copies
    )

    return {
        "message": "Book added successfully",
        "book": new_book
    }


@router.get("/books")
def list_books():
    books = get_all_books()
    return {"books": books}


@router.get("/books/search")
def search_for_books(query: str = Query(..., min_length=1)):
    books = search_books(query)

    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    return {"books": books}

@router.get("/books/overdue")
def list_overdue_books():
    overdue_books = get_overdue_books()

    return {
        "overdue_books": overdue_books,
        "count": len(overdue_books)
    }