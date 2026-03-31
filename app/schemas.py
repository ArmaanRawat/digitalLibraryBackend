from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int 
    name: str
    email: EmailStr
    role: str

class AurthorCreate(BaseModel):
    name: str

class CategoryCreate(BaseModel):
    name: str

class BookCreate(BaseModel):
    title: str
    author: str
    category: str
    total_copies: int


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    category: str
    available_copies: int


class BorrowRequest(BaseModel):
    user_id: int


class BorrowResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: str
    due_date: str
    status: str

class ReturnRequest(BaseModel):
    user_id: int

class FineResponse(BaseModel):
    borrow_record_id: int
    amount: float
    paid: bool