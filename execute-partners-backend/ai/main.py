import json
import logging
import os
from typing import Optional

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient

from chatbot_logic import ArticleWriterModule, get_bot_response
from llm_service import call_gemini
from llm_session import call_gemini as session_call_gemini, close_conversation

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "execute-partners-database")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "articles")

client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client[DATABASE_NAME]
articles_col = db[COLLECTION_NAME]

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://www.executepartners.com",
    "https://execute-partners-community.vercel.app",
]
allowed_origins = os.getenv("ALLOWED_ORIGINS", ",".join(default_origins)).split(",")

app = FastAPI(title="Execute Partners AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}


def text_result(value):
    if isinstance(value, dict):
        return {"text": value.get("text", str(value))}
    return {"text": str(value) if value is not None else ""}


def get_article_by_id(article_id):
    if not article_id:
        return None
    try:
        return articles_col.find_one({"_id": ObjectId(article_id)})
    except Exception as e:
        logger.error("Error fetching article: %s", e)
        return None


def get_comment_content_by_id(comment_id):
    if not comment_id:
        return None
    try:
        if not isinstance(comment_id, ObjectId):
            comment_id = ObjectId(comment_id)
        article = db.articles.find_one({"comments._id": comment_id}, {"comments.$": 1})
        if article and article.get("comments"):
            return article["comments"][0]["content"]
    except Exception as e:
        logger.error("Error fetching comment: %s", e)
    return None


def compute_engagement(article, weight_likes=1, weight_comments=2, weight_shares=3):
    likes_count = len(article.get("likes", []))
    comments_count = len(article.get("comments", []))
    shares_count = article.get("claps", 0)
    views_count = article.get("views", 0)
    if views_count > 0:
        return (
            weight_likes * likes_count
            + weight_comments * comments_count
            + weight_shares * shares_count
            + 4 * views_count
        )
    return weight_likes * likes_count + weight_comments * comments_count + weight_shares * shares_count


class ChatRequest(BaseModel):
    session_id: str
    message: str
    text: Optional[str] = ""


class SummarizeRequest(BaseModel):
    article_id: Optional[str] = ""
    comment_id: Optional[str] = ""
    delete: Optional[bool] = False


class TitleRequest(BaseModel):
    category: str


class UserInput(BaseModel):
    message: str
    session_id: str


class PostArticleRequest(BaseModel):
    article: str
    session_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Execute Partners Unified AI API"}


@app.post("/chat")
async def chat_with_bot(body: ChatRequest):
    session_id = body.session_id
    user_message = body.message
    text = body.text or ""

    if not session_id or not user_message:
        return JSONResponse({"detail": "session_id and message are required."}, status_code=400)

    if session_id not in SESSIONS:
        SESSIONS[session_id] = ArticleWriterModule()

    writer_module = SESSIONS[session_id]
    bot_result = get_bot_response(user_message, text, writer_module)

    if isinstance(bot_result, dict):
        response_text = bot_result.get("text", str(bot_result))
    else:
        response_text = bot_result

    if writer_module.stage == "idle" and response_text and "Here is your complete article" in response_text:
        SESSIONS.pop(session_id, None)

    return {"session_id": session_id, "response": response_text}


@app.post("/summarize")
async def summarize_article(body: SummarizeRequest):
    article_id = (body.article_id or "").strip()
    comment_id = (body.comment_id or "").strip()
    delete = body.delete or False
    response_data = {}

    if article_id:
        article = get_article_by_id(article_id)
        if not article:
            return JSONResponse({"error": f"Article with ID {article_id} not found."}, status_code=404)

        title = article.get("title", "")
        meta_desc = article.get("meta", {}).get("description", "")
        response_data["title"] = title

        if not delete and article.get("summary") and article.get("overview"):
            response_data["article_summary"] = text_result(article.get("summary"))
            response_data["article_overview"] = text_result(article.get("overview", ""))
            response_data["summary"] = text_result(article.get("summary"))
            response_data["message"] = "Article summary and overview already exists."
        else:
            if delete:
                articles_col.update_one(
                    {"_id": ObjectId(article_id)},
                    {"$unset": {"summary": "", "overview": ""}},
                )
            summary_meta = call_gemini("summary", context_vars={"text": title + " " + meta_desc}) if meta_desc else {"text": ""}
            overview = call_gemini("overview", context_vars={"text": title + " " + meta_desc}) if meta_desc else {"text": ""}
            summary_text = summary_meta.get("text", "") if isinstance(summary_meta, dict) else summary_meta
            overview_text = overview.get("text", "") if isinstance(overview, dict) else overview
            articles_col.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": {"summary": summary_text, "overview": overview_text}},
            )
            response_data["article_summary"] = text_result(summary_text)
            response_data["article_overview"] = text_result(overview_text)
            response_data["summary"] = text_result(summary_text)
            response_data["message"] = "Article summary saved to database."

    if comment_id:
        comment_content = get_comment_content_by_id(comment_id)
        if not comment_content:
            response_data["comment_summary"] = ""
            response_data["comment_message"] = "Comment not found."
        else:
            article_with_comment = db.articles.find_one({"comments._id": ObjectId(comment_id)})
            comment_obj = None
            if article_with_comment:
                comment_obj = next(
                    (c for c in article_with_comment.get("comments", []) if c["_id"] == ObjectId(comment_id)),
                    None,
                )
            if not comment_obj:
                response_data["comment_summary"] = ""
                response_data["comment_message"] = "Comment object not found."
            elif not delete and comment_obj.get("summary"):
                response_data["comment_summary"] = text_result(comment_obj.get("summary"))
                response_data["comment_message"] = "Comment summary already exists."
            else:
                if delete:
                    db.articles.update_one(
                        {"comments._id": ObjectId(comment_id)},
                        {"$unset": {"comments.$.summary": ""}},
                    )
                comment_summary = call_gemini("summary", context_vars={"text": comment_content})
                summary_text = comment_summary.get("text", "") if isinstance(comment_summary, dict) else comment_summary
                db.articles.update_one(
                    {"comments._id": ObjectId(comment_id)},
                    {"$set": {"comments.$.summary": summary_text}},
                )
                response_data["comment_summary"] = text_result(summary_text)
                response_data["comment_message"] = "Comment summary saved to database."

    return response_data


@app.get("/trending")
def get_trending_articles(
    weight_likes: int = 1,
    weight_comments: int = 2,
    weight_shares: int = 3,
    top_n: int = 5,
):
    articles = list(articles_col.find({"isPublished": True}))
    for article in articles:
        article["engagement_score"] = compute_engagement(
            article, weight_likes, weight_comments, weight_shares
        )
    sorted_articles = sorted(articles, key=lambda x: x["engagement_score"], reverse=True)
    result = [
        {
            "title": a["title"],
            "slug": a.get("slug"),
            "engagement_score": a["engagement_score"],
            "likes": len(a.get("likes", [])),
            "comments": len(a.get("comments", [])),
            "shares": a.get("claps", 0),
            "views": a.get("views"),
        }
        for a in sorted_articles[:top_n]
    ]
    return {"trending": result}


@app.post("/generate_title")
async def generate_title(body: TitleRequest):
    generated = call_gemini(
        "category_title_generation",
        context_vars={"category": body.category},
        max_tok=2000,
    )
    return {"title": text_result(generated)}


@app.post("/generate_article")
async def generate_article(body: UserInput):
    if body.message.lower() == "exit":
        return {"message": "Exiting the conversation."}
    if body.message.lower() == "reset":
        close_conversation(body.session_id)
        return {"message": "Conversation reset."}
    response = session_call_gemini(
        body.session_id,
        "generate_article",
        context_vars={"userInput": body.message},
    )
    return {"response": response}


@app.post("/post_article")
async def post_article(body: PostArticleRequest):
    if not body.article:
        return JSONResponse({"error": "Article content is required."}, status_code=400)
    response = session_call_gemini(
        body.session_id,
        "post_article",
        context_vars={"GeneratedArticle": body.article},
        use_history=False,
    )
    cleaned = response.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = {"raw": cleaned}
    return {"response": parsed}
