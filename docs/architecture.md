# ITR Filing App - Architecture Overview

## Document Processing Flow

```mermaid
flowchart TD
    A["AuthPage (Login)"] --> B["ITR Selection Page"]
    B --> C["Document Upload Page"]
    C --> D["Progress Dashboard"]
    
    C -->|"Files + metadata"| E["POST /api/v1/itr/upload"]
    E -->|"Reads bytes in-memory"| F["Processing Engine"]
    
    F --> G{"MD5 Check Blob Storage"}
    G -->|"Exists & Complete"| H["Skip → Mark Completed"]
    G -->|"Missing/Incomplete"| I["Queue for Processing"]
    
    I --> J["Async Semaphore Pool (batch=5)"]
    J --> K["PDF → 200 DPI Images (in-memory)"]
    K --> L["Gemini API + Dynamic Prompt"]
    L --> M["Save JSON to Blob Storage"]
    
    D <----|"SSE Stream"| N["GET /api/v1/itr/progress/{session_id}"]
    N --> F
    
    style A fill:#4f46e5,color:#fff
    style B fill:#4f46e5,color:#fff
    style C fill:#4f46e5,color:#fff
    style D fill:#4f46e5,color:#fff
    style F fill:#8b5cf6,color:#fff
    style J fill:#8b5cf6,color:#fff
```

## Tech Stack Decisions

- **In-Memory Buffer**: Using `io.BytesIO` and `fitz` stream for zero-disk persistence.
- **Concurrency**: `asyncio.Semaphore(5)` to manage Gemini API rate limits.
- **Real-time**: `sse-starlette` for server-to-client progress broadcasting.
- **Caching**: MD5-based deduplication on Azure Blob Storage.
- **Routing**: `react-router-dom` for the guided user journey.
