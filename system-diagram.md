# GrooveBot System Diagram

```mermaid
flowchart TD
    subgraph Browser["Browser (Client)"]
        UI["index.html\nGrooveBot Chat UI"]
    end

    subgraph Flask["Flask Server · localhost:5000  (app.py)"]
        ROUTE_INDEX["GET /\nServes index.html"]
        ROUTE_GEN["POST /generate\nHandles mood query"]
    end

    subgraph LLMProxyLib["LLMProxy Client (llmproxy/main.py)"]
        UPLOAD["upload_file()\nrequest_type: add"]
        GENERATE["generate()\nrequest_type: call\nRAG enabled"]
    end

    subgraph DataFiles["Local Data (data/)"]
        HAPPY["happy.txt"]
        SAD["sad.txt"]
    end

    subgraph ExternalService["External LLM Service (LLMPROXY_ENDPOINT)"]
        RAG_STORE["RAG Vector Store\nsession_id scoped"]
        LLM["LLM  ·  gpt-4o-mini\nSystem prompt + RAG context"]
    end

    %% Startup flow
    HAPPY -- on startup --> UPLOAD
    SAD   -- on startup --> UPLOAD
    UPLOAD -- "POST (multipart)\nx-api-key + file" --> RAG_STORE

    %% Request flow
    UI -- "POST /generate\n{ query }" --> ROUTE_GEN
    ROUTE_GEN -- "proxy.generate()" --> GENERATE
    GENERATE -- "POST (JSON)\nquery + rag_threshold=0.8\nrag_k=5" --> LLM
    LLM -- "retrieve top-5 chunks" --> RAG_STORE
    RAG_STORE -- "relevant song context" --> LLM
    LLM -- "song recommendations" --> GENERATE
    GENERATE -- "JSON response" --> ROUTE_GEN
    ROUTE_GEN -- "{ result: ... }" --> UI

    %% Page load
    Browser -- "GET /" --> ROUTE_INDEX
    ROUTE_INDEX -- "index.html" --> Browser

    classDef file fill:#f0ead6,stroke:#c8b87a
    classDef ext  fill:#d6e8f0,stroke:#5a9abf
    class HAPPY,SAD file
    class RAG_STORE,LLM ext
```    

## Component Summary

| Component | Role |
|-----------|------|
| `index.html` | Chat UI — collects user mood, displays song recommendations |
| `app.py` | Flask server — serves UI, proxies queries, uploads data on startup |
| `llmproxy/main.py` | HTTP client — wraps the external LLM endpoint (file upload + generation) |
| `data/happy.txt`, `data/sad.txt` | Song knowledge base uploaded to RAG on startup |
| External LLM service | Stores RAG vectors, retrieves relevant songs, generates recommendations |

## Key Flows

**Startup** — `app.py` scans `data/`, uploads every `.txt` file to the external service's RAG store under `SESSION_ID = "my-app-session"`.

**User query** — Browser POSTs mood text → Flask calls `proxy.generate()` → service retrieves the top-5 most relevant song chunks (threshold 0.8) → LLM produces a recommendation → response bubbles back to chat UI.

**Safety guard** — System prompt instructs the LLM to detect depression/suicidal signals and redirect to a medical professional instead of recommending songs.
