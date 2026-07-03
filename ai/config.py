import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

ARTICLE = """

"""

_model = None


def get_model():
    global _model
    if _model is not None:
        return _model

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set. Add it in Render env for ep-ai-api."
        )

    genai.configure(api_key=api_key)
    _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model
