from fastapi import FastAPI, Query, File, UploadFile, Form, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, or_, select, func
from typing import List, Optional, Generator
from dotenv import load_dotenv
import os


app = FastAPI(title="Book Search API")

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")



# creating book model
class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    publisher: str
    year: str
    image_url: Optional[str] = None


# create engine & tables
engine = create_engine(DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)



# Generate session:
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@app.get("/books/search", response_model=List[Book])
def search_books(q: Optional[str] = Query(None),
                 page: int = Query(1, ge=1),
                 size: int = Query(10, ge=1, le=50),
                 session: Session = Depends(get_session)):

    skip = (page - 1) * size
    stmt = select(Book)

    search_term = (q or "").strip()
    if search_term:
        stmt = stmt.where(
            or_(
                Book.title.ilike(f"%{search_term}%"),
                Book.author.ilike(f"%{search_term}%"),
                Book.publisher.ilike(f"%{search_term}%"),
            )
        )

    stmt = stmt.offset(skip).limit(size)
    results = session.exec(stmt).all()
    return results


@app.post("/books/add", response_model=Book)
async def add_books(title: str = Form(...),
                    author: str = Form(...),
                    publisher: str = Form(...),
                    year: str = Form(...),
                    image: UploadFile = File(None),
                    session: Session = Depends(get_session)
                    ):
    image_url = None
    if image:
        os.makedirs("static/images", exist_ok=True)
        file_path = f"static/images/{image.filename}"
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_url = f"/images/{image.filename}"

    new_book = Book(
        title=title,
        author=author,
        publisher=publisher,
        year=year,
        image_url=image_url
    )

    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book
