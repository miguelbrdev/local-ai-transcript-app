# AGENTS.md — AI Transcript App

## Project Overview

AI-powered voice transcription app: FastAPI backend (Whisper STS + LLM cleaning) + React/Vite frontend. Devcontainer-first with Ollama as default LLM provider.

## Architecture

- **Backend** (`backend/`): FastAPI on port 8000. Entry: `backend/app.py`. Core logic: `backend/transcription.py` (`TranscriptionService`).
- **Frontend** (`frontend/`): React 19 + Vite on port 3000. Entry: `frontend/src/main.tsx` → `App.tsx`.
- **Ollama**: Runs as separate Docker service on port 11434 (hostname `ollama` inside devcontainer).
- **Communication**: Frontend proxies `/api` to backend via Vite config. No hardcoded URLs in frontend code.

## Commands

### Start (two terminals required)

```bash
# Terminal 1 - Backend
cd backend && uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 600

# Terminal 2 - Frontend
cd frontend && pnpm run dev
```

### Frontend

```bash
pnpm run dev          # dev server
pnpm run build        # tsc + vite build
pnpm run type-check   # tsc --noEmit
pnpm run lint         # eslint (fail on warnings)
pnpm run lint:fix     # eslint --fix
pnpm run format       # prettier --write
pnpm run format:check # prettier --check
```

### Backend

```bash
uv sync               # install/update deps (run after branch switch)
uv run pytest -q      # run tests (from repo root, or cd backend first)
```

### Benchmarks

```bash
python3 benchmarks/benchmark_transcription.py -m medium -a benchmarks/benchmarkTest.wav --runs 5
```

## Key Constraints

- **Node.js >= 24** required (enforced in `frontend/package.json`).
- **Python >= 3.12** required (enforced in `backend/pyproject.toml`).
- Frontend uses **pnpm** (not npm) for package management. Devcontainer installs pnpm globally.
- Backend uses **uv** for dependency management (not pip).
- `--timeout-keep-alive 600` is required on uvicorn for long audio processing.
- Vite proxy timeout is 600000ms (10 min) for `/api` routes.

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/status` | Health check, returns model info |
| GET | `/api/system-prompt` | Returns default LLM cleaning prompt |
| POST | `/api/transcribe` | Upload audio file → Whisper transcription |
| POST | `/api/clean` | Send text → LLM cleaning (body: `{text, system_prompt?}`) |

## Configuration

- `backend/.env` controls all runtime config. Created automatically from `.env.example` in devcontainer.
- `LLM_BASE_URL`: defaults to `http://ollama:11434/v1` (inside devcontainer). Use `http://localhost:11434/v1` for manual setup.
- `WHISPER_MODEL`: defaults to `base.en`.
- `LLM_MODEL`: defaults to `gemma3:4b`.
- System prompt for LLM cleaning: `backend/system_prompt_hr.txt` (loaded by `transcription.py:15-16`).

## Testing

- Tests live in `backend/tests/`. Only backend has tests.
- `conftest.py` adds `backend/` to `sys.path` — no `PYTHONPATH` needed when running from repo root.
- Tests use dummy modules to avoid loading real ML models.
- Run: `backend/.venv/bin/pytest -q` or `cd backend && uv run pytest -q`.

## Devcontainer

- `post-create.sh` handles all setup: waits for Ollama, creates `.env`, installs deps (uv + pnpm), downloads `gemma3:4b`.
- Docker Compose defines two services: `app` (workspace) and `ollama` (LLM server).
- Forwarded ports: 8000 (FastAPI), 3000 (Vite), 11434 (Ollama).
- Requires minimum 4 CPUs, 16GB RAM, 32GB storage.

## Branches

This repo uses checkpoint branches for progressive learning. `main` is the base vanilla app. `modifications` is the branch to work with. The user is modifying this project on this branch to make it on his own and the objective is to add it to his portfolio. Other branches (`checkpoint-*`) add agentic workflows, PydanticAI, MCP, etc, but won´t be modified or used. Always check current branch before assuming available features.

## File Boundaries

- `backend/transcription.py`: `TranscriptionService` class — Whisper loading, transcription, LLM cleaning, device auto-detect (CUDA → CPU fallback).
- `backend/app.py`: FastAPI app, CORS, lifespan init, 4 endpoints.
- `frontend/src/App.tsx`: Main React orchestrator — state management, audio/text flows.
- `frontend/vite.config.ts`: Dev server config, `/api` proxy to `localhost:8000`.

## Gotchas

- LLM cleaning has a fallback: if LLM call fails, returns raw Whisper text (`transcription.py:95`).
- Whisper uses `condition_on_previous_text=False` — no context carryover between segments.
- CORS allows `localhost:3000` and `localhost:5173` only.
- Temp audio files in `/api/transcribe` are cleaned up in `finally` block.
- Frontend `tsconfig.json` excludes `vite.config.ts` and `eslint.config.js` from type checking.
- Path alias `@/*` maps to `./src/*` in frontend.
