from pydantic import BaseModel
from typing import Optional


class Isbn(BaseModel):
    id:str

class Book(BaseModel):
    id: Optional[int]
    title: Optional[str]
    authors: Optional[str]
    publishDate: Optional[str]
    description: Optional[str]
    stock: Optional[int]=1
    image: Optional[str]
    isbn: Optional[str]
    