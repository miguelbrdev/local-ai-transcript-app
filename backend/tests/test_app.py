import sys
import types
from types import SimpleNamespace

import pytest

# Inject dummy dependencies used by transcription/app before importing app
if "ctranslate2" not in sys.modules:
    mod = types.ModuleType("ctranslate2")
    mod.get_cuda_device_count = lambda: 0
    sys.modules["ctranslate2"] = mod
if "faster_whisper" not in sys.modules:
    mod = types.ModuleType("faster_whisper")

    class DummyWhisperModel:
        def __init__(self, *a, **kw):
            pass

        def transcribe(self, *a, **kw):
            return [], None

    mod.WhisperModel = DummyWhisperModel
    sys.modules["faster_whisper"] = mod
if "openai" not in sys.modules:
    mod = types.ModuleType("openai")

    class DummyOpenAI:
        def __init__(self, base_url=None, api_key=None):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kw: SimpleNamespace(
                        choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
                    )
                )
            )
            self.models = SimpleNamespace(list=lambda: None)

    mod.OpenAI = DummyOpenAI
    sys.modules["openai"] = mod

import app as app_module
from app import CleanRequest


@pytest.mark.asyncio
async def test_get_status_initializing():
    app_module.service = None
    res = await app_module.get_status()
    assert res["status"] == "initializing"


@pytest.mark.asyncio
async def test_get_system_prompt_ok():
    class DummyService:
        def get_default_system_prompt(self):
            return "PROMPT X"

    app_module.service = DummyService()
    res = await app_module.get_system_prompt()
    assert res == {"default_prompt": "PROMPT X"}


@pytest.mark.asyncio
async def test_clean_endpoint_uses_service():
    class DummyService:
        def clean_with_llm(self, text, system_prompt=None):
            return "cleaned:" + text

    app_module.service = DummyService()
    req = CleanRequest(text="hola")
    res = await app_module.clean_text(req)
    assert res == {"success": True, "text": "cleaned:hola"}
