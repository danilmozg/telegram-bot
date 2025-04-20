from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DBPost(Base):
    """Модель SQLAlchemy для хранения постов в базе данных."""
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(Text)
    user_id = Column(Integer)

class Joke(BaseModel):
    """Модель Pydantic для валидации данных шутки."""
    value: str
    id: Optional[str] = None
    categories: Optional[List[str]] = None

class Post(BaseModel):
    """Модель Pydantic для валидации данных поста."""
    id: int
    title: str
    body: str
    user_id: int = Field(..., alias="userId")

    class Config:
        validate_by_name = True
