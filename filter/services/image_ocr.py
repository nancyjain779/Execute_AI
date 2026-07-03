# from PIL import Image
# from io import BytesIO
# import requests
# from transformers import pipeline

# class ImageOCRService:
#     def __init__(self):
#         self.pipe = pipeline("image-text-to-text", model="ds4sd/SmolDocling-256M-preview")

#     def extract_text(self, image_url: str) -> str:
#         response = requests.get(image_url)
#         image = Image.open(BytesIO(response.content)).convert("RGB")

#         result = self.pipe([{
#             "role": "user",
#             "content": [
#                 {"type": "image", "image": image},
#                 {"type": "text", "text": "extract text from image"}
#             ]
#         }])
#         return result[0]['generated_text'][1]['content'] if result else ""

from PIL import Image
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
class ImageClassifier:
    def __init__(self):
        self.prompt = prompt = """
Classify the image into toxic and non toxic or safe or not safe.
Output format:
toxic:boolean
non_toxic:boolean
if text is present in image extract text from image :
Output format:
toxic:boolean
non_toxic:boolean
text:string
Give output in json format and dont include anything in output
"""
    def classify(self, image: Image.Image) -> str:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            [self.prompt,image]
        )
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        try:
            return result
        except Exception:
            return {"raw": text}