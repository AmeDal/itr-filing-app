import asyncio
from typing import List, Optional, Sequence, Tuple

import fitz

PDF_TEXT_THRESHOLD = 50


class PDFPasswordRequired(Exception):
    """Raised when a PDF is encrypted and requires a password."""


def _open_pdf(file_bytes: bytes, password: Optional[str] = None) -> fitz.Document:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        if "encrypted" in str(exc).lower():
            raise PDFPasswordRequired("This PDF is password protected.") from exc
        raise

    if doc.is_encrypted:
        if not password or not doc.authenticate(password):
            doc.close()
            raise PDFPasswordRequired(
                "Invalid or missing password for encrypted PDF.")

    return doc


def _get_pdf_page_count_sync(file_bytes: bytes) -> int:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    try:
        return len(doc)
    finally:
        doc.close()


def _render_pdf_pages_sync(file_bytes: bytes,
                           page_numbers: Sequence[int],
                           dpi: int = 200) -> List[Tuple[int, bytes]]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    try:
        rendered_pages: List[Tuple[int, bytes]] = []
        for page_index in page_numbers:
            page = doc[page_index]
            pix = page.get_pixmap(dpi=dpi)
            rendered_pages.append((page_index, pix.tobytes("png")))
        return rendered_pages
    finally:
        doc.close()


def _extract_pdf_payload_sync(
    file_bytes: bytes,
    password: Optional[str] = None,
    text_threshold: int = PDF_TEXT_THRESHOLD,
) -> Tuple[bool, str, List[bytes]]:
    doc = _open_pdf(file_bytes, password=password)
    try:
        all_text = ""
        try:
            for page in doc:
                all_text += page.get_text()
        except ValueError as exc:
            if "encrypted" in str(exc).lower():
                raise PDFPasswordRequired(
                    "This PDF is password protected.") from exc
            raise

        stripped_text = all_text.strip()
        if len(stripped_text) >= text_threshold:
            return True, all_text, []

        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            images.append(pix.tobytes("png"))
        return False, "", images
    finally:
        doc.close()


async def get_pdf_page_count(file_bytes: bytes) -> int:
    return await asyncio.to_thread(_get_pdf_page_count_sync, file_bytes)


async def render_pdf_pages(file_bytes: bytes,
                           page_numbers: Sequence[int],
                           dpi: int = 200) -> List[Tuple[int, bytes]]:
    return await asyncio.to_thread(_render_pdf_pages_sync, file_bytes,
                                   tuple(page_numbers), dpi)


async def extract_pdf_payload(
    file_bytes: bytes,
    password: Optional[str] = None,
    text_threshold: int = PDF_TEXT_THRESHOLD,
) -> Tuple[bool, str, List[bytes]]:
    return await asyncio.to_thread(_extract_pdf_payload_sync, file_bytes,
                                   password, text_threshold)
