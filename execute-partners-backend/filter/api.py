# from fastapi import FastAPI
# from pydantic import BaseModel
# from model_loader import ModelLoader
# from services.text_filter import TextFilterService
# from services.image_ocr import ImageOCRService
# from typing import Optional
# from fastapi.responses import JSONResponse
# import logging

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         logging.StreamHandler()
#     ]
# )

# logger = logging.getLogger(__name__)

# app = FastAPI()
# logger.info("Starting FastAPI app...")

# model_loader = ModelLoader()
# logger.info("ModelLoader initialized.")

# text_filter_service = TextFilterService(model_loader)
# logger.info("TextFilterService initialized.")

# image_ocr_service = ImageOCRService()
# logger.info("Image OCR image initialized")


# class InputData(BaseModel):
#     text: Optional[str] = None
#     image_url: Optional[str] = None

# @app.post("/filtercomment")
# async def filter_comment(input_data: InputData):
#     logger.info("Received request: %s", input_data)
#     final_text = ""
#     # Case 1: Extract text from image
#     if input_data.image_url:
#         logger.info("Image URL provided: %s", input_data.image_url)
#         try:
#             logger.info("Fetching image from URL...")
#             final_text = image_ocr_service.extract_text(input_data.image_url)
#             logger.info("Generated text: %s", final_text)

#         except Exception as e:
#             logger.error("Image processing failed: %s", str(e))
#             return JSONResponse(status_code=400, content={"error": f"Image processing failed: {str(e)}"})

#     # Case 2: Use provided text
#     elif input_data.text:
#         logger.info("Text input provided.")
#         final_text = input_data.text
#     else:
#         logger.warning("No input provided.")
#         return JSONResponse(status_code=400, content={"error": "Either 'text' or 'image_url' must be provided."})

#     try:
#         logger.info("Processing text through TextFilterService...")
#         results = text_filter_service.process_text(final_text)
#         results["extracted_text"] = final_text
#         logger.info("Text filtering complete. Results: %s", results)
#         return results

#     except Exception as e:
#         logger.exception("Text filtering failed.")
#         return JSONResponse(status_code=500, content={"error": f"Text filtering failed: {str(e)}"})

# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting Uvicorn server...")
#     uvicorn.run(app, host="0.0.0.0", port=3000)

from flask import Flask, request, jsonify
from flask_cors import CORS
from model_loader import ModelLoader
from services.text_filter import TextFilterService
from services.llm_text_filter import ArticleClassifier
from services.image_ocr import ImageClassifier
from typing import Optional
from PIL import Image
import logging
import io
import os
import cv2
import numpy as np
import base64

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
logger.info("Starting Flask app...")

model_loader = ModelLoader()
logger.info("ModelLoader initialized.")

text_filter_service = TextFilterService(model_loader)
logger.info("TextFilterService initialized.")

image_classifier = ImageClassifier()
logger.info("ImageClassifier initialized.")

def blur_image(pil_image: Image.Image) -> Image.Image:
    """Convert PIL image to OpenCV, apply Gaussian blur, and return as PIL."""
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    blurred_cv = cv2.GaussianBlur(cv_image, (25, 25), 0)
    blurred_pil = Image.fromarray(cv2.cvtColor(blurred_cv, cv2.COLOR_BGR2RGB))
    return blurred_pil

@app.route("/filtercomment", methods=["POST","OPTIONS"])
def filter_comment():
    text = request.form.get("text")
    image_url = request.form.get("image_url")
    article = request.form.get("article", "false").lower() == "true"
    image_file = request.files.get("image_file")
    logger.info("Received request: text=%s, image_url=%s, article=%s, image_file=%s", text, image_url, article, image_file.filename if image_file else None)
    final_text = ""

    # Case 1: Image file upload
    if image_file:
        try:
            logger.info("Processing uploaded image file: %s", image_file.filename)
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            result = image_classifier.classify(image)
            
            if result.get("text"):
                result['toxic_result'] = text_filter_service.process_text(result.get("text"))

            logger.info("Image classification result: %s", result)

            # Check if content is toxic or unsafe
            is_toxic = result.get("toxic") is True or not result.get("toxic_result", {}).get("safe", True)
            
            if is_toxic:
                logger.info("Toxic content detected. Blurring image.")
                blurred_image = blur_image(image)

                # Compose annotation message
                if not result.get("text"):
                     message = "The image contains some toxic content"
                else:
                    toxic_result = result.get("toxic_result", {})
                    exclude_keys = {"safe", "identity_hate_custom", "not_identity_hate_custom"}
                    filtered = {k: v for k, v in toxic_result.items() if k not in exclude_keys}
                    if filtered:
                        max_label = max(filtered, key=filtered.get)
                        message = "The image contains some toxic content"
                    else:
                        message = "The image contains some toxic content"

                # Encode blurred image to base64
                buffer = io.BytesIO()
                blurred_image.save(buffer, format="JPEG")
                encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

                result["blurred_image_base64"] = encoded_image
                result["blurred"] = True
                result["alert_message"] = message
            else:
                result["blurred"] = False

            return jsonify(content={"image_classification": result})

        except Exception as e:
            logger.error("Image file processing failed: %s", str(e))
            return jsonify(status_code=400, content={"error": f"Image file processing failed: {str(e)}"})

    # Case 2: Extract text from image URL
    if image_url:
        logger.info("Image URL provided: %s", image_url)
        try:
            logger.info("Fetching image from URL...")
            # You need to implement image_ocr_service.extract_text or use image_classifier if that's your OCR
            final_text = image_classifier.extract_text(image_url)
            logger.info("Generated text: %s", final_text)
        except Exception as e:
            logger.error("Image processing failed: %s", str(e))
            return jsonify({"error": f"Image processing failed: {str(e)}"}), 400

    # Case 3: Use provided text
    elif text:
        logger.info("Text input provided.")
        final_text = text
    else:
        logger.warning("No input provided.")
        return jsonify({"error": "Either 'text', 'image_url', or 'image_file' must be provided."}), 400

    try:
        logger.info("Processing text through TextFilterService...")
        if article:
            logger.info("Classifying article...")
            classifier = ArticleClassifier(final_text)
            result = classifier.classify()
            logger.info("Article classification complete: %s", final_text)
            return jsonify(result)
        else:
            results = text_filter_service.process_text(final_text)
            results["extracted_text"] = final_text
            logger.info("Text filtering complete. Results: %s", results)
            return jsonify(results)

    except Exception as e:
        logger.exception("Text filtering failed.")
        return jsonify({"error": f"Text filtering failed: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))

