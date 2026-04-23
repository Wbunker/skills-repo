# Assistants API

## STATUS: DEPRECATED

**Shutdown date: August 26, 2026.**

The Responses API has achieved feature parity with the Assistants API. OpenAI recommends migrating all Assistants API usage to the Responses API before the shutdown date.

---

## What It Was

The Assistants API provided a higher-abstraction stateful conversation system with persistent Threads, server-managed conversation lifecycle, and built-in tools (file search, code interpreter).

---

## Core Objects

### Assistant
Configuration object stored on OpenAI servers.
```
POST /v1/assistants
{
  "model": "gpt-4o",
  "name": "Support Bot",
  "instructions": "You are a helpful support assistant.",
  "tools": [{"type": "file_search"}, {"type": "code_interpreter"}],
  "tool_resources": {
    "file_search": {"vector_store_ids": ["vs_..."]}
  }
}
```

### Thread
Persistent conversation container. Holds all messages.
```
POST /v1/threads
{}  # empty — or provide initial messages

POST /v1/threads/{thread_id}/messages
{
  "role": "user",
  "content": "What's in the uploaded document?",
  "attachments": [{"file_id": "file_...", "tools": [{"type": "file_search"}]}]
}
```

### Run
Execution of an assistant on a thread. Async lifecycle.
```
POST /v1/threads/{thread_id}/runs
{"assistant_id": "asst_..."}

GET /v1/threads/{thread_id}/runs/{run_id}
# Poll until status = "completed" | "failed" | "requires_action"
```

**Run statuses:** `queued` → `in_progress` → `completed` / `failed` / `requires_action` (for function calls) / `expired` / `cancelled`

### Vector Store
Storage for file search.
```
POST /v1/vector_stores
{"name": "Support Docs"}

POST /v1/vector_stores/{id}/files
{"file_id": "file_..."}
```
Files are automatically parsed, chunked, embedded, and indexed on upload.

---

## Built-in Tools

### file_search
- Semantic + keyword search over uploaded files
- Up to 10,000 files per vector store
- Up to 10,000 files per assistant
- Billed: $0.10 per 1,000 queries

### code_interpreter
- Python execution in a secure sandbox
- Max 20 files attached
- Useful for: data analysis, math, image manipulation, file conversion
- Billed per session

### Function calling
- Same pattern as Chat Completions
- `requires_action` run status triggers caller to execute function and submit result

---

## File Limits Summary

| Tool | Max Files |
|------|-----------|
| code_interpreter | 20 files |
| file_search (per vector store) | 10,000 files |
| file_search (per assistant) | 10,000 files |

---

## Migration to Responses API

| Assistants API | Responses API equivalent |
|----------------|-------------------------|
| Thread | `previous_response_id` chaining |
| Run (async polling) | Synchronous response or streaming |
| file_search tool | `{"type": "file_search", "vector_store_ids": [...]}` |
| code_interpreter tool | `{"type": "code_interpreter"}` |
| Assistant instructions | `instructions` parameter |
| Vector Store | Same Vector Store API (shared) |

The Responses API does not require polling — responses are synchronous or streaming, eliminating the queued→in_progress→completed lifecycle.
