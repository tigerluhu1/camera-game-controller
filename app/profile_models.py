from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class Binding:
    action_name: str
    input_type: str = "key"
    input_value: str = ""
    trigger_mode: str = "tap"
    cooldown_ms: int = 0
    enabled: bool = True

    @classmethod
    def from_dict(cls, action_name: str, data: dict) -> "Binding":
        return cls(
            action_name=action_name,
            input_type=data.get("input_type", "key"),
            input_value=data.get("input_value", ""),
            trigger_mode=data.get("trigger_mode", "tap"),
            cooldown_ms=int(data.get("cooldown_ms", 0)),
            enabled=bool(data.get("enabled", True)),
        )

    def to_dict(self) -> dict:
        return {
            "action_name": self.action_name,
            "input_type": self.input_type,
            "input_value": self.input_value,
            "trigger_mode": self.trigger_mode,
            "cooldown_ms": self.cooldown_ms,
            "enabled": self.enabled,
        }


@dataclass(slots=True)
class Preset:
    game_name: str
    preset_name: str
    character_name: str = "default"
    notes: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    bindings: dict[str, Binding] = field(default_factory=dict)
    runtime_overrides: dict[str, float | int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Preset":
        bindings = {
            action_name: Binding.from_dict(action_name, binding_data)
            for action_name, binding_data in data.get("bindings", {}).items()
        }
        return cls(
            game_name=data["game_name"],
            character_name=data.get("character_name", "default") or "default",
            preset_name=data["preset_name"],
            notes=data.get("notes", ""),
            updated_at=data.get("updated_at", datetime.now(UTC).isoformat()),
            bindings=bindings,
            runtime_overrides=dict(data.get("runtime_overrides", {})),
        )

    def to_dict(self) -> dict:
        return {
            "game_name": self.game_name,
            "character_name": self.character_name or "default",
            "preset_name": self.preset_name,
            "notes": self.notes,
            "updated_at": self.updated_at,
            "bindings": {
                action_name: binding.to_dict()
                for action_name, binding in sorted(self.bindings.items())
            },
            "runtime_overrides": dict(sorted(self.runtime_overrides.items())),
        }
