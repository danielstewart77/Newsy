from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import JSON, Column, Integer, Text, String, create_engine, func, TIMESTAMP, cast, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

class NewsMetadata(BaseModel):
    source: str = Field(description="The source of the article")
    topic: str = Field(description="The topic of the article, eg. AI, Crypto, Cyber Security, etc.")
    url: str = Field(description="URL of the article")
    date: str = Field(description="Date of the article in the format YYYY-MM-DD")

    class Config:
        extra = "forbid"

class Article(BaseModel):
    title: str = Field(description="Title of the article")
    summary: str = Field(description="A short 3-4 sentence summary of the article")
    body: str = Field(description="The entire body of the article")
    metadata: NewsMetadata = Field(description="Metadata of the article")

    class Config:
        extra = "forbid"

class Articles(BaseModel):
    articles: list[Article]

    class Config:
        extra = "forbid"

class ArticleDTO(BaseModel):
    title: str
    summary: str
    body: str
    tts_audio: str

Base = declarative_base()

class DbArticle(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text_embedding_3_large = Column(Vector(dim=1536), nullable=True)
    title = Column(Text, nullable=False)
    summery = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=False)
    article_metadata = Column(JSON, nullable=False)
    created_by = Column(String, nullable=False)
    created = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    read = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Articles(id={self.id}, created_by={self.created_by})>"