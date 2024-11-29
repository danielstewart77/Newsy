from services.database import DatabaseService
from services.utilities import sanitize_filename
from sources import NewsAggregator
from models.article import Articles, ArticleDTO, DbArticle
from services.openai import structured_chat_completion
from services.tts import call_tts_api, TTSRequest, read_news
from typing import Dict
from quart import url_for, jsonify, send_from_directory
from services.interpret import interpret_chat, Tools, ParameterProperty
from models.message import Message
import logging
import hypercorn
import quart_cors
from quart import Quart, request
from uuid import uuid4
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Quart app
app = Quart("newsy")
app.secret_key = str(uuid4())

# Enable CORS for the app
app = quart_cors.cors(app)

# News Aggregator instance
aggregator = NewsAggregator()

# Dictionary to hold audio streams temporarily
audio_store: Dict[str, bytes] = {}

# Serve Swagger UI using static files and a simple route
@app.route("/api/docs")
async def swagger_ui():
    return await send_from_directory(os.path.join(app.root_path, "static"), "swagger.html")

# Serve Swagger YAML file
@app.route("/api/swagger.yaml")
async def swagger_yaml():
    return await send_from_directory(app.root_path, "swagger.yaml")

# Quart route to get AI news
@app.route("/api/ai")
async def get_ai_news(*args, **kwargs):
    """Get AI News
    ---
    responses:
      200:
        description: A list of AI news articles
    """
    # Fetch AI news
    ai_news = aggregator.fetch_ai_news()
    articles = structured_chat_completion(
        text=ai_news,
        llm_model="gpt-4o-2024-08-06",
        feature_model=Articles
    )

    for article in articles.articles:
        # combine the title, body, and metadata into a single JSON object
        article_metadata = article.model_dump()
        article_metadata.update(article.metadata)

        # add each article to the db
        dbArticle = DbArticle(
            title=article.title,
            summery=article.summary,
            body=article.body,
            metadata_=article.metadata.model_dump(),
            article_metadata=article_metadata,
            created_by="daniel",
            read=False
        )
        # get db session
        session = DatabaseService().get_session()
        session.add(dbArticle)
        session.commit()
        session.close()

async def get_news_from_db(topic: str = None):
    # get all articles from the db
    session = DatabaseService().get_session()

    query = session.query(DbArticle).filter(DbArticle.read == False)  # Filter by read = False

    if topic is not None:
        query = query.filter(DbArticle.metadata['topic'].astext == topic)  # Filter by metadata topic

    article = query.first()

    if article:
        article.read = True
        session.commit()  # Commit the changes to the database

    session.close()
    return article

async def get_news(*args, **kwargs):
    # get the requested news from the database  
    article = await get_news_from_db()

    # Process articles asynchronously
    #article_dtos = []
    #for article in articles:
    audio = await read_news(article)
    article_dto = ArticleDTO(
        title=article.title,
        summary=article.summery,
        body=article.body,
        tts_audio=audio
    )
    #article_dtos.append(article_dto)

    # Prepare the response with articles and audio URLs
    response_data = []
    async with app.app_context():
        #for article in article_dtos:
        if article_dto.tts_audio:
            article_dto.tts_audio = url_for('static', filename=f"audio/{article_dto.tts_audio}", _external=True)
        response_data.append(article_dto.model_dump())

    return jsonify(response_data)

@app.route("/chat", methods=["POST"])
async def chat():
    data = await request.get_json()  # Extract JSON from the POST request body
    messages = data.get("messages", [])
    # Example usage
    properties = []
    properties.append(
        ParameterProperty(
            type="string", 
            description="the topic of the news desired, eg: AI, infosec, crypto", 
            name="topic"))
    properties.append(
        ParameterProperty(
            type="string", 
            description="the time range of the news desired, eg: last week, last month",
            name="daterange",
            default="today"))
    properties.append(
        ParameterProperty(
            type="integer", 
            description="the number of articles to return", 
            name="limit",
            default=10))

    tools_instance = Tools.create(
        name="get_news",
        description="When a user askes for news",
        parameters_type="object",
        properties=properties,
        required=[],
        additional_properties=False
    )

    functions = {
        "get_news": get_news
    }

    return await interpret_chat(messages, tools_instance, functions)


# Run Hypercorn server
if __name__ == "__main__":
    import asyncio
    config = hypercorn.Config()
    config.bind = ["0.0.0.0:8000"]
    asyncio.run(hypercorn.asyncio.serve(app, config))
