from pydantic import BaseModel, Field

class Article(BaseModel):
    title: str = Field(description="Title of the article")
    summary: str = Field(description="A short 3-4 sentence summary of the article")
    body: str = Field(description="The entire body of the article")

    class Config:
        extra = "forbid"

class Articles(BaseModel):
    articles: list[Article]

    class Config:
        extra = "forbid"