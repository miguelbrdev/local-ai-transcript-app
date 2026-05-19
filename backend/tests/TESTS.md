# Backend tests

This file explains how to run the backend unit tests.

## Prerequisites

- A Python virtual environment in `backend/.venv` with `pytest` and `pytest-asyncio` installed.
- To create it (if needed):

```bash
cd backend
python -m venv .venv
.venv/bin/python -m pip install -U pip setuptools
.venv/bin/python -m pip install pytest pytest-asyncio
```

## Run the tests

- Run all tests from the repository root:

```bash
backend/.venv/bin/pytest -q
```

- Or use the venv Python:

```bash
backend/.venv/bin/python -m pytest -q
```

- If you get `ModuleNotFoundError` for `app` or `transcription`, try:

```bash
PYTHONPATH=backend backend/.venv/bin/pytest -q
```

## What the tests check

- `backend/tests/test_transcription_service.py`:
  - Tests `TranscriptionService` behavior: device detection, joining segments, and `clean_with_llm` success and fallback.
  - The test injects dummy modules (`ctranslate2`, `faster_whisper`, `openai`) to avoid loading real models.

- `backend/tests/test_app.py`:
  - Tests `app` module functions: `get_status`, `get_system_prompt`, and `clean_text`.
  - The tests replace `service` with simple dummy objects and use `pytest-asyncio` for async tests.
