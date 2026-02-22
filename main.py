from fastapi import FastAPI, Depends, HTTPException, Query, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlmodel import select, SQLModel, Session
from typing import List
import os
import shutil

from database import engine, get_session
from models import Book

os.makedirs("static/images", exist_ok=True)

SQLModel.metadata.create_all(engine)

app = FastAPI(title="Book Search API with SQLModel")

app.mount("/images", StaticFiles(directory="static/images"), name="images")

# Dependency درست (اینطوری بهتر کار می‌کنه)
def get_db_session():
    return Depends(get_session)


@app.get("/books/search", response_model=List[Book])
def search_books(
    q: str | None = Query(None, max_length=100, min_length=3),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_session)
):
    statement = select(Book)

    if q:                               # ← اینجا مشکل اصلی بود
        q_clean = q.lower().strip()
        statement = statement.where(
            (Book.title.ilike(f"%{q_clean}%")) |
            (Book.author.ilike(f"%{q_clean}%")) |
            (Book.publisher.ilike(f"%{q_clean}%"))
        )

    # pagination همیشه اعمال بشه (حتی وقتی q نیست)
    statement = statement.offset((page - 1) * size).limit(size)

    results = session.exec(statement).all()
    return results


@app.post("/books/add", response_model=Book)
async def add_books(
    title: str = Form(...),
    author: str = Form(...),
    publisher: str = Form(...),
    year: str = Form(...),
    image: UploadFile | None = File(None),          # ← Noneable کردمش
    session: Session = Depends(get_session)
):
    image_url = None

    if image:
        os.makedirs("static/images", exist_ok=True)
        file_path = f"static/images/{image.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_url = f"/images/{image.filename}"

    book = Book(
        title=title,
        author=author,
        publisher=publisher,
        year=year,
        image_url=image_url
    )

    session.add(book)
    session.commit()
    session.refresh(book)

    return book