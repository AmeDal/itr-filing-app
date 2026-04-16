import asyncio
import logging

import fitz
import google.genai as genai
from google.genai import types
from google.genai.errors import APIError

from backend.schemas.extraction_schema import (AadharExtractionResponse,
                                               PanExtractionResponse)
from backend.settings import get_settings

logger = logging.getLogger(__name__)


def get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


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

                if hasattr(e, 'response') and hasattr(e.response, 'json'):
                    try:
                        resp_json = e.response.json()
                        details = resp_json.get("error", {}).get("details", [])
                        for detail in details:
                            if detail.get(
                                    "@type"
                            ) == "type.googleapis.com/google.rpc.RetryInfo":
                                retry_delay = detail.get("retryDelay", "")
                                if retry_delay.endswith("s"):
                                    delay = float(retry_delay[:-1])
                                    break
                    except Exception:
                        logger.exception(
                            "Could not extract retry logic directly from response JSON"
                        )

                logger.warning(
                    f"Google Gemini rate limit hit (429). Retrying in {delay:.2f} seconds... (Attempt {attempt+1}/{max_retries})"
                )
                await asyncio.sleep(delay)
            else:
                raise


async def extract_pan_data(image_bytes: bytes,
                           mime_type: str) -> PanExtractionResponse:
    client = get_client()
    settings = get_settings()
    prompt = "Analyze the provided document(s). If they do not represent a valid PAN card, set is_error to true and explain why. Otherwise, set is_error to false and extract the details into extraction_data. Respond with a strict JSON. Ensure all dates are YYYY-MM-DD. Separate names accurately."

    contents = []
    if mime_type == "application/pdf":
        doc = fitz.open(stream=image_bytes, filetype="pdf")
        zoom = 2.77
        mat = fitz.Matrix(zoom, zoom)
        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            png_bytes = pix.tobytes("png")
            contents.append(
                types.Part.from_bytes(data=png_bytes, mime_type="image/png"))
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
                               mime_type: str) -> AadharExtractionResponse:
    client = get_client()
    settings = get_settings()
    prompt = "Analyze the provided document(s). If they do not represent a valid Aadhar card, set is_error to true and explain why. Otherwise, set is_error to false and extract the details into extraction_data. Respond with a strict JSON. Ensure all dates are YYYY-MM-DD."

    contents = []
    if mime_type == "application/pdf":
        doc = fitz.open(stream=image_bytes, filetype="pdf")
        zoom = 2.77
        mat = fitz.Matrix(zoom, zoom)
        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            png_bytes = pix.tobytes("png")
            contents.append(
                types.Part.from_bytes(data=png_bytes, mime_type="image/png"))
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
