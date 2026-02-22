from typing import Optional
from sqlmodel import SQLModel, Field


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    author: str
    publisher: str
    year: str = Field(max_length=4)
    image_url: Optional[str] = Field(default=None, max_length=500, nullable=True)
