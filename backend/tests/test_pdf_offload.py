from types import SimpleNamespace

import pytest

from backend.services import pdf_service
from backend.services.itr_processing_service import ITRProcessingService, SessionManager


@pytest.mark.asyncio
async def test_extract_pdf_payload_offloads_to_thread(monkeypatch):
    called = {}

    def fake_sync(file_bytes, password=None, text_threshold=50):
        called["sync_args"] = (file_bytes, password, text_threshold)
        return True, "hello world", []

    async def fake_to_thread(func, *args):
        called["thread_func"] = func
        return func(*args)

    monkeypatch.setattr(pdf_service, "_extract_pdf_payload_sync", fake_sync)
    monkeypatch.setattr(pdf_service.asyncio, "to_thread", fake_to_thread)

    contains_text, extracted_text, images = await pdf_service.extract_pdf_payload(
        b"pdf-bytes", password="secret")

    assert called["thread_func"] is fake_sync
    assert called["sync_args"] == (b"pdf-bytes", "secret", 50)
    assert contains_text is True
    assert extracted_text == "hello world"
    assert images == []


@pytest.mark.asyncio
async def test_render_pdf_pages_offloads_to_thread(monkeypatch):
    called = {}

    def fake_sync(file_bytes, page_numbers, dpi=200):
        called["sync_args"] = (file_bytes, page_numbers, dpi)
        return [(1, b"png-page")]

    async def fake_to_thread(func, *args):
        called["thread_func"] = func
        return func(*args)

    monkeypatch.setattr(pdf_service, "_render_pdf_pages_sync", fake_sync)
    monkeypatch.setattr(pdf_service.asyncio, "to_thread", fake_to_thread)

    rendered_pages = await pdf_service.render_pdf_pages(b"pdf-bytes", [1], dpi=144)

    assert called["thread_func"] is fake_sync
    assert called["sync_args"] == (b"pdf-bytes", (1,), 144)
    assert rendered_pages == [(1, b"png-page")]


@pytest.mark.asyncio
async def test_itr_processing_service_uses_pdf_helper(monkeypatch):
    session_id = "session-1"
    user_id = "user-1"
    ay = "AY-2025-26"
    doc_type = "FORM_16"
    file_name = "form16.pdf"
    file_bytes = b"pdf-bytes"
    file_hash = ITRProcessingService.calculate_file_hash(file_bytes)

    SessionManager._sessions = {}
    SessionManager._listeners = {}
    SessionManager.create_session(
        session_id,
        user_id,
        [{
            "file_name": file_name,
            "file_hash": file_hash,
            "type": doc_type,
        }],
    )

    captured = {"pages": [], "page_count_calls": 0, "render_calls": 0}

    async def fake_get_existing_hash_for_slot(*args, **kwargs):
        return None

    async def fake_add_or_update_document(*args, **kwargs):
        return None

    async def fake_list_existing_pages(*args, **kwargs):
        return []

    async def fake_get_pdf_page_count(pdf_bytes):
        captured["page_count_calls"] += 1
        assert pdf_bytes == file_bytes
        return 2

    async def fake_render_pdf_pages(pdf_bytes, page_numbers, dpi=200):
        captured["render_calls"] += 1
        assert pdf_bytes == file_bytes
        assert list(page_numbers) == [0, 1]
        assert dpi == 200
        return [(0, b"page-0"), (1, b"page-1")]

    async def fake_process_single_page(session, user, assessment_year, kind,
                                       current_hash, page_index, total_pages,
                                       img_bytes):
        captured["pages"].append(
            (session, user, assessment_year, kind, current_hash, page_index,
             total_pages, img_bytes))
        SessionManager.update_progress(session,
                                       current_hash,
                                       page_index,
                                       total_pages,
                                       status="completed_page")

    monkeypatch.setattr(
        "backend.services.itr_processing_service.BlobStorageService",
        SimpleNamespace(
            get_existing_hash_for_slot=fake_get_existing_hash_for_slot,
            list_existing_pages=fake_list_existing_pages,
        ),
    )
    monkeypatch.setattr("backend.services.itr_processing_service.filing_service",
                        SimpleNamespace(
                            add_or_update_document=fake_add_or_update_document,
                            update_extraction_status=fake_add_or_update_document,
                        ))
    monkeypatch.setattr("backend.services.itr_processing_service.get_pdf_page_count",
                        fake_get_pdf_page_count)
    monkeypatch.setattr("backend.services.itr_processing_service.render_pdf_pages",
                        fake_render_pdf_pages)
    monkeypatch.setattr(ITRProcessingService, "_process_single_page",
                        fake_process_single_page)

    await ITRProcessingService.process_document(session_id, user_id, ay, doc_type,
                                                file_name, file_bytes)

    assert captured["page_count_calls"] == 1
    assert captured["render_calls"] == 1
    assert [page[5] for page in captured["pages"]] == [0, 1]
