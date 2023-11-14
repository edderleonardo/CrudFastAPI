from typing import Optional

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import Query
from pydantic import BaseModel
from pydantic import Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    reating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(None, title="ID is not needed")
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "HP1",
                "author": "Author 1",
                "description": "Book Description",
                "rating": 2,
                "published_date": 2029,
            }
        }


BOOKS = [
    Book(1, 'Computer Science Pro', 'John Doe', 'A book about computer science', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'John Doe', 'A greatbook!', 5, 2030),
    Book(3, 'Master Endpoints', 'John Doe', 'A awesome book', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    "Get all books"
    return BOOKS


@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(gt=0)):
    "Get a book by id"
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book does not exist")


@app.get("/books/")
async def read_book_by_rating(rating: int = Query(None, gt=0, lt=6)):
    "Get a book by rating"
    books_by_rating = [book for book in BOOKS if book.rating == rating]
    if not books_by_rating:
        raise HTTPException(status_code=404, detail="Books not found by rating")
    return books_by_rating


@app.get("/books/published/")
async def read_book_by_published_date(published_date: int = Query(None, gt=1999, lt=2031)):
    "Get a book by published date"
    books_by_published_date = [book for book in BOOKS if book.published_date == published_date]
    if not books_by_published_date:
        raise HTTPException(status_code=404, detail="Books not found by published date")
    return books_by_published_date


@app.post("/create-book")
async def create_book(book_request: BookRequest):
    "Create a new book"
    new_book = Book(**book_request.model_dump())
    new_book.id = find_book_id()
    BOOKS.append(new_book)
    return book_request


def find_book_id():
    return 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1


@app.put("/books/update_book")
async def update_book(book_request: BookRequest):
    "Update a book"
    book_changed = False
    for id in range(len(BOOKS)):
        if BOOKS[id].id == book_request.id:
            BOOKS[id] = book_request
            book_changed = True
            return book_request
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}")
async def delete_book(book_id: int = Path(gt=0)):
    "Delete a book"
    for id in range(len(BOOKS)):
        if BOOKS[id].id == book_id:
            del BOOKS[id]
            return {"message": "Book deleted"}
    return {"message": "Book not found"}

