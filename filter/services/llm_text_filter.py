import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=api_key)

def get_working_model():
    """
    Automatically find a Gemini model that supports generateContent.
    Falls back safely if the preferred model is missing.
    """
    preferred_models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash-002",
        "gemini-1.5-pro-002",
        "gemini-1.0-pro",  # older fallback
    ]

    try:
        models = genai.list_models()
        model_names = [m.name for m in models]
        logger.info(f"Available models from Google: {model_names}")

        # return first preferred model that exists
        for pm in preferred_models:
            if pm in model_names:
                logger.info(f"Using Gemini model: {pm}")
                return pm

        # fallback to first model that supports generation
        for m in models:
            if "generateContent" in getattr(m, "supported_methods", []):
                logger.info(f"Using fallback model: {m.name}")
                return m.name

    except Exception as e:
        logger.error(f"Could not list models: {e}")

    # Last fallback
    return "gemini-2.0-flash"


class ArticleClassifier:
    def __init__(self, article):
        self.article = article
        self.model_name = get_working_model()

    def classify(self):
        prompt = f"""You are an AI assistant. Your task is to classify the article on labels: toxic, severe_toxic, obscene, threat, insult, identity_hate.
Output Format (JSON only, no explanation):
{{
  "toxic": float,
  "severe_toxic": float,
  "obscene": float,
  "threat": float,
  "insult": float,
  "identity_hate": float
}}
ONLY output the JSON object. Do NOT include any explanation, thoughts, or extra text.
Given article: {self.article}
"""

        model = genai.GenerativeModel(self.model_name)
        logger.info(f"Sending request to Gemini model: {self.model_name}")

        try:
            response = model.generate_content(prompt)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"error": str(e)}

        # Extract raw text output
        text = response.text.strip().replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(text)
        except Exception:
            result = {"error": "Invalid JSON format", "raw": text}

        # Determine safety based on score thresholds
        result["safe"] = all(
            result.get(label, 0) < 0.5
            for label in ["toxic", "severe_toxic", "obscene", "insult", "identity_hate"]
        )

        # Add token usage (if available)
        usage = getattr(response, "usage_metadata", None)
        if usage:
            result["token_usage"] = {
                "input_tokens": usage.prompt_token_count,
                "output_tokens": usage.candidates_token_count,
                "total_tokens": usage.total_token_count,
            }

        return result
