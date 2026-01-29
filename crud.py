from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel


books = [
    {"id": 1, "title": "1984", "author": "George Orwell"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 4, "title": "Moby Dick", "author": "Herman Melville"},
]

app = FastAPI()

@app.get("/books/")
def get_book():
    return books


@app.get("/book/{book_id}")
def get_book_by_id(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


class Book(BaseModel):
    id: int
    title: str  
    author: str

@app.post("/books")
def create_book(book: Book):
    new_book = book.model_dump()
    books.append(new_book)
    return new_book
