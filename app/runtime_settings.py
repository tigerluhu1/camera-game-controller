from __future__ import annotations

import json
from pathlib import Path


RUNTIME_DEFAULTS = {
    "mouse_sensitivity": 1.0,
    "mouse_deadzone": 0,
    "mouse_smoothing": 0.0,
    "camera_device": 0,
}


def _coerce_runtime_settings(values: dict | None) -> dict[str, float | int]:
    data = dict(RUNTIME_DEFAULTS)
    source = values or {}
    data["mouse_sensitivity"] = float(source.get("mouse_sensitivity", data["mouse_sensitivity"]))
    data["mouse_deadzone"] = int(source.get("mouse_deadzone", data["mouse_deadzone"]))
    data["mouse_smoothing"] = float(source.get("mouse_smoothing", data["mouse_smoothing"]))
    data["camera_device"] = int(source.get("camera_device", data["camera_device"]))
    return data


class RuntimeSettingsStore:
    def __init__(self, root: Path | str):
        self.root = Path(root)

    @property
    def path(self) -> Path:
        return self.root / "runtime.json"

    def load(self) -> dict[str, float | int]:
        if not self.path.exists():
            return dict(RUNTIME_DEFAULTS)
        return _coerce_runtime_settings(json.loads(self.path.read_text(encoding="utf-8")))

    def save(self, values: dict | None) -> Path:
        resolved = _coerce_runtime_settings(values)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(resolved, indent=2), encoding="utf-8")
        return self.path


def resolve_runtime_settings(
    defaults: dict | None,
    overrides: dict | None,
) -> dict[str, float | int]:
    resolved = _coerce_runtime_settings(defaults)
    for key, value in (overrides or {}).items():
        if key not in RUNTIME_DEFAULTS:
            continue
        resolved[key] = _coerce_runtime_settings({key: value})[key]
    return resolved
