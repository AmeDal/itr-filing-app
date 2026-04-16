import asyncio
import logging
from typing import Optional

import fitz
import google.genai as genai
from google.genai import types
from google.genai.errors import APIError

from backend.schemas.extraction_schema import (AadharExtractionResponse,
                                               PanExtractionResponse)
from backend.settings import get_settings

logger = logging.getLogger(__name__)

# Text extraction threshold (characters) to determine if PDF has readable content
PDF_TEXT_THRESHOLD = 50


class PDFPasswordRequired(Exception):
    """Raised when a PDF is encrypted and requires a password."""
    pass


def get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


def get_pdf_content(image_bytes: bytes, password: Optional[str] = None) -> tuple[bool, list]:
    """
    Process PDF content and return whether text was extracted and content parts.
    
    If encrypted, attempts to unlock with provided password.
    Raises PDFPasswordRequired if it remains locked.
    """
    try:
        doc = fitz.open(stream=image_bytes, filetype="pdf")
    except Exception as e:
        if "encrypted" in str(e).lower():
            raise PDFPasswordRequired("This PDF is password protected.")
        raise e

    if doc.is_encrypted:
        if not password or not doc.authenticate(password):
            raise PDFPasswordRequired("Invalid or missing password for encrypted PDF.")

    # Extract all text from the PDF
    all_text = ""
    try:
        for page in doc:
            all_text += page.get_text()
    except ValueError as e:
        if "encrypted" in str(e).lower():
            raise PDFPasswordRequired("This PDF is password protected.")
        raise e

    # Check if extracted text exceeds threshold
    if len(all_text.strip()) >= PDF_TEXT_THRESHOLD:
        logger.info(
            f"PDF contains {len(all_text.strip())} characters of text. Using direct text extraction."
        )
        return True, [all_text]

    # Fall back to image conversion if text is insufficient
    logger.info(
        f"PDF contains only {len(all_text.strip())} characters. Falling back to image conversion."
    )
    content_parts = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        png_bytes = pix.tobytes("png")
        content_parts.append(
            types.Part.from_bytes(data=png_bytes, mime_type="image/png")
        )
    return False, content_parts


async def _generate_content_with_retry(client,
                                       model,
                                       contents,
                                       config,
                                       max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except APIError as e:
            if attempt < max_retries - 1 and e.code == 429:
                delay = 15 * (attempt + 1)
                logger.warning(
                    f"Google Gemini rate limit hit (429). Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            else:
                raise


async def extract_pan_data(image_bytes: bytes,
                           mime_type: str,
                           password: Optional[str] = None) -> PanExtractionResponse:
    client = get_client()
    settings = get_settings()
    prompt = "Analyze the provided document(s). If they do not represent a valid PAN card, set is_error to true and explain why. Otherwise, set is_error to false and extract the details into extraction_data. Respond with a strict JSON. Ensure all dates are YYYY-MM-DD. Separate names accurately."

    contents = []
    if mime_type == "application/pdf":
        _, pdf_contents = get_pdf_content(image_bytes, password)
        contents.extend(pdf_contents)
    else:
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

    contents.append(prompt)

    response = await _generate_content_with_retry(
        client=client,
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PanExtractionResponse,
        ),
    )
    return PanExtractionResponse.model_validate_json(response.text)


async def extract_aadhar_data(image_bytes: bytes,
                              mime_type: str,
                              password: Optional[str] = None) -> AadharExtractionResponse:
    client = get_client()
    settings = get_settings()
    prompt = "Analyze the provided document(s). If they do not represent a valid Aadhar card, set is_error to true and explain why. Otherwise, set is_error to false and extract the details into extraction_data. Respond with a strict JSON. Ensure all dates are YYYY-MM-DD."

    contents = []
    if mime_type == "application/pdf":
        _, pdf_contents = get_pdf_content(image_bytes, password)
        contents.extend(pdf_contents)
    else:
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

    contents.append(prompt)

    response = await _generate_content_with_retry(
        client=client,
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AadharExtractionResponse,
        ),
    )
    return AadharExtractionResponse.model_validate_json(response.text)
