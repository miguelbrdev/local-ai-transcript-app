import sys
import types
from types import SimpleNamespace

# Inject minimal dummy modules before importing `transcription`
if "ctranslate2" not in sys.modules:
    mod = types.ModuleType("ctranslate2")
    mod.get_cuda_device_count = lambda: 0
    sys.modules["ctranslate2"] = mod
if "faster_whisper" not in sys.modules:
    mod = types.ModuleType("faster_whisper")

    class DummyWhisperModel:
        def __init__(self, *a, **kw):
            pass

        def transcribe(
            self,
            audio_file,
            beam_size=None,
            language=None,
            condition_on_previous_text=None,
        ):
            return [SimpleNamespace(text="Hola"), SimpleNamespace(text="mundo")], None

    mod.WhisperModel = DummyWhisperModel
    sys.modules["faster_whisper"] = mod
if "openai" not in sys.modules:
    mod = types.ModuleType("openai")

    class DummyOpenAI:
        def __init__(self, base_url=None, api_key=None):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kw: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content="Texto limpio")
                            )
                        ]
                    )
                )
            )
            self.models = SimpleNamespace(list=lambda: None)

    mod.OpenAI = DummyOpenAI
    sys.modules["openai"] = mod

import transcription


def test_system_prompt_non_empty():
    assert isinstance(transcription.SYSTEM_PROMPT, str)
    assert transcription.SYSTEM_PROMPT.strip() != ""


def test_get_device_and_compute_cpu(monkeypatch):
    monkeypatch.setattr(transcription.ctranslate2, "get_cuda_device_count", lambda: 0)
    svc = transcription.TranscriptionService("m", "u", "k", "lm")
    assert svc._get_device_and_compute() == ("cpu", "int8")


def test_transcribe_joins_segments(monkeypatch):
    class DummyWhisper:
        def __init__(self, *a, **kw):
            pass

        def transcribe(self, *a, **kw):
            return [SimpleNamespace(text="Hola"), SimpleNamespace(text="mundo")], None

    monkeypatch.setattr(transcription, "WhisperModel", DummyWhisper)
    monkeypatch.setattr(transcription.ctranslate2, "get_cuda_device_count", lambda: 0)
    svc = transcription.TranscriptionService("m", "u", "k", "lm")
    assert svc.transcribe("dummy.wav") == "Hola mundo"


def test_clean_with_llm_returns_cleaned(monkeypatch):
    monkeypatch.setattr(transcription.ctranslate2, "get_cuda_device_count", lambda: 0)
    svc = transcription.TranscriptionService("m", "u", "k", "lm")
    svc.llm_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kw: SimpleNamespace(
                    choices=[
                        SimpleNamespace(message=SimpleNamespace(content="Texto limpio"))
                    ]
                )
            )
        )
    )
    assert svc.clean_with_llm("texto sucio") == "Texto limpio"


def test_clean_with_llm_on_error_returns_input(monkeypatch):
    monkeypatch.setattr(transcription.ctranslate2, "get_cuda_device_count", lambda: 0)
    svc = transcription.TranscriptionService("m", "u", "k", "lm")

    def raise_exc(**kw):
        raise Exception("LLM fail")

    svc.llm_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=raise_exc))
    )
    assert svc.clean_with_llm("texto") == "texto"
