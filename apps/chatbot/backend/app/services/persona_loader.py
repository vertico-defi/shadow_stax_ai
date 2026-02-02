from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import validate

from shared.logging.logger import get_logger

logger = get_logger("persona-loader")

_CACHE: Dict[str, Any] | None = None


def _persona_dir() -> Path:
    return Path(__file__).resolve().parents[5] / "shared" / "persona"


def load_default_persona() -> Dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    persona_dir = _persona_dir()
    schema_path = persona_dir / "persona.schema.json"
    persona_path = persona_dir / "default_persona.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    persona = json.loads(persona_path.read_text(encoding="utf-8"))
    validate(instance=persona, schema=schema)

    _CACHE = persona
    logger.info("persona_loaded name=%s", persona.get("name"))
    return persona
