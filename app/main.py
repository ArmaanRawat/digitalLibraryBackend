from fastapi import FastAPI
from app.routes import auth, books, borrow, fines

app = FastAPI(title="Digital Library Backend")

app.include_router(auth.router, tags=["Auth"])
app.include_router(books.router, tags=["Books"])
app.include_router(borrow.router, tags=["Borrow"])
app.include_router(fines.router, tags=["Fines"])

@app.get("/")
def home():
    return {"message": "Welcome to the Digital Library Backend 🚀"}