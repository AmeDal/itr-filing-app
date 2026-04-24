import asyncio
from typing import List, Optional, Tuple

import google.genai as genai
from google.genai import types
from google.genai.errors import APIError

from backend.logger import logger
from backend.services.pdf_service import PDFPasswordRequired, extract_pdf_payload
from backend.schemas.extraction_schema import AadharExtractionResponse, PanExtractionResponse
from backend.settings import get_settings


def get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


async def get_pdf_content(image_bytes: bytes,
                          password: Optional[str] = None) -> Tuple[bool, List]:
    """
    Process PDF content and return whether text was extracted and content parts.
    """
    contains_text, extracted_text, page_images = await extract_pdf_payload(
        image_bytes, password)

    if contains_text:
        logger.info(
            f"PDF contains {len(extracted_text.strip())} chars of text. Using direct text extraction."
        )
        return True, [extracted_text]

    logger.info(
        f"PDF contains {len(extracted_text.strip())} chars. Falling back to image conversion."
    )
    return False, [
        types.Part.from_bytes(data=png_bytes, mime_type="image/png")
        for png_bytes in page_images
    ]


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
                    f"Gemini rate limit (429). Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                raise


async def extract_pan_data(
        image_bytes: bytes,
        mime_type: str,
        password: Optional[str] = None) -> PanExtractionResponse:
    client = get_client()
    settings = get_settings()
    prompt = (
        "Analyze the provided document(s). If they do not represent a valid PAN card, "
        "set is_error to true and explain why. Otherwise, set is_error to false and "
        "extract the details into extraction_data. Respond with a strict JSON. "
        "Ensure all dates are YYYY-MM-DD. Separate names accurately.")

    contents = []
    if mime_type == "application/pdf":
        _, pdf_contents = await get_pdf_content(image_bytes, password)
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


async def extract_aadhar_data(
        image_bytes: bytes,
        mime_type: str,
        password: Optional[str] = None) -> AadharExtractionResponse:
    client = get_client()
    settings = get_settings()
    prompt = (
        "Analyze the provided document(s). If they do not represent a valid Aadhar card, "
        "set is_error to true and explain why. Otherwise, set is_error to false and "
        "extract the details into extraction_data. Respond with a strict JSON. "
        "Ensure all dates are YYYY-MM-DD.")

    contents = []
    if mime_type == "application/pdf":
        _, pdf_contents = await get_pdf_content(image_bytes, password)
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
