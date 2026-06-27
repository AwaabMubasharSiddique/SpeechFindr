import os
from threading import Lock

from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


API_TITLE = "SpeechFindr API"
DEFAULT_MODEL = "whisper-large-v3-turbo"
CACHE_TTL_SECONDS = 3600
HTTP_RETRIES = 3

GROQ_TIER = (os.getenv("GROQ_TIER") or "").strip().lower()
if not GROQ_TIER:
    GROQ_TIER = "paid" if (os.getenv("GROQ_PAID_API_KEY") or "").strip() else "free"
IS_PAID_TIER = GROQ_TIER in ("paid", "dev", "developer")

UPLOAD_CHUNK_SECONDS = _env_int("UPLOAD_CHUNK_SECONDS", 600)

TRANSLATION_BATCH_SIZE = _env_int("TRANSLATION_BATCH_SIZE", 25)
TRANSLATION_GROUP_SENTENCES = _env_bool("TRANSLATION_GROUP_SENTENCES", True)


def _apply_tier_values() -> None:
    global UPLOAD_MAX_PARALLEL, TRANSLATION_MAX_PARALLEL
    global TRANSLATION_TOKENS_PER_MIN, TRANSLATION_PREFER_GOOGLE
    UPLOAD_MAX_PARALLEL = _env_int("UPLOAD_MAX_PARALLEL", 12 if IS_PAID_TIER else 4)
    TRANSLATION_MAX_PARALLEL = _env_int("TRANSLATION_MAX_PARALLEL", 8 if IS_PAID_TIER else 2)
    TRANSLATION_TOKENS_PER_MIN = _env_int("TRANSLATION_TOKENS_PER_MIN", 250_000 if IS_PAID_TIER else 10_000)
    TRANSLATION_PREFER_GOOGLE = _env_bool("TRANSLATION_PREFER_GOOGLE", not IS_PAID_TIER)


def apply_tier(tier: str) -> None:
    global GROQ_TIER, IS_PAID_TIER
    GROQ_TIER = (tier or "free").strip().lower()
    IS_PAID_TIER = GROQ_TIER in ("paid", "dev", "developer")
    _apply_tier_values()


_apply_tier_values()
TRANSLATION_GROUP_MAX_CHARS = _env_int("TRANSLATION_GROUP_MAX_CHARS", 280)
TRANSLATION_GROUP_MAX_CUES = _env_int("TRANSLATION_GROUP_MAX_CUES", 6)

GOOGLE_TRANSLATE_BATCH_LINES = _env_int("GOOGLE_TRANSLATE_BATCH_LINES", 64)
GOOGLE_TRANSLATE_CHUNK_LINES = _env_int("GOOGLE_TRANSLATE_CHUNK_LINES", 64)
GOOGLE_TRANSLATE_CHUNK_CHARS = _env_int("GOOGLE_TRANSLATE_CHUNK_CHARS", 8000)
GOOGLE_TRANSLATE_MAX_PARALLEL = _env_int("GOOGLE_TRANSLATE_MAX_PARALLEL", 4)
GOOGLE_TRANSLATE_MIN_INTERVAL_MS = _env_int("GOOGLE_TRANSLATE_MIN_INTERVAL_MS", 150)

YOUTUBE_TRUST_AUTO_CAPTIONS = _env_bool("YOUTUBE_TRUST_AUTO_CAPTIONS", False)

TTS_ENGINE = (os.getenv("TTS_ENGINE") or "edge").strip().lower()
TTS_MAX_CHARS = _env_int("TTS_MAX_CHARS", 20000)

TRANSCRIPT_CACHE: dict = {}
CACHE_MAX_ENTRIES = _env_int("CACHE_MAX_ENTRIES", 200)
_CACHE_LOCK = Lock()


def cache_put(key: str, payload) -> None:
    import time

    now = time.time()
    with _CACHE_LOCK:
        if len(TRANSCRIPT_CACHE) >= CACHE_MAX_ENTRIES:
            expired = [k for k, v in TRANSCRIPT_CACHE.items() if (now - v["ts"]) >= CACHE_TTL_SECONDS]
            for k in expired:
                TRANSCRIPT_CACHE.pop(k, None)
            overflow = len(TRANSCRIPT_CACHE) - CACHE_MAX_ENTRIES + 1
            if overflow > 0:
                for k in sorted(TRANSCRIPT_CACHE, key=lambda k: TRANSCRIPT_CACHE[k]["ts"])[:overflow]:
                    TRANSCRIPT_CACHE.pop(k, None)
        TRANSCRIPT_CACHE[key] = {"ts": now, "payload": payload}


TRANSLATION_TOGGLE = 0
TRANSLATION_LOCK = Lock()
