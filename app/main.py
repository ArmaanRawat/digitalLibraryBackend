from fastapi import FastAPI
from app.routers import users, books, borrow, fines

app = FastAPI(title="Digital Library Backend")

# Include routers
app.include_router(users.router, tags=["Users"])
app.include_router(books.router, tags=["Books"])
app.include_router(borrow.router, tags=["Borrow"])
app.include_router(fines.router, tags=["Fines"])


@app.get("/")
def home():
    return {"message": "Welcome to the Digital Library Backend 🚀"}