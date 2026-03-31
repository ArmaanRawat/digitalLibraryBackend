from fastapi import FastAPI, HTTPException
from app.models import create_tables
from app.routes import auth, books, borrow, fines


create_tables() # Ensure tables are created before the app starts

app = FastAPI()

# Include routers for different functionalities
app.include_router(auth.router, tags=["Auth"])
app.include_router(books.router, tags=["Books"])
app.include_router(borrow.router, tags=["Borrow"])
app.include_router(fines.router, tags=["Fines"])


@app.get("/")
def home():
    return {"message": "Welcome to the Digital Library Backend, yupp its up 🚀"}