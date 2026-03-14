from __future__ import annotations

import json
from pathlib import Path

from app.profile_models import Preset


def _slugify(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "_" for char in value.strip())
    parts = [part for part in cleaned.split("_") if part]
    return "_".join(parts) or "default"


class ProfileStore:
    def __init__(self, root: Path | str):
        self.root = Path(root)

    def preset_path(self, game_name: str, character_name: str, preset_name: str) -> Path:
        return self.root / _slugify(game_name) / _slugify(character_name or "default") / f"{_slugify(preset_name)}.json"

    def save_preset(self, preset: Preset) -> Path:
        path = self.preset_path(preset.game_name, preset.character_name, preset.preset_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(preset.to_dict(), indent=2), encoding="utf-8")
        return path

    def load_preset(self, game_name: str, character_name: str, preset_name: str) -> Preset:
        path = self.preset_path(game_name, character_name, preset_name)
        data = json.loads(path.read_text(encoding="utf-8"))
        return Preset.from_dict(data)

    def list_games(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(path.name for path in self.root.iterdir() if path.is_dir())

    def list_characters(self, game_name: str) -> list[str]:
        game_path = self.root / _slugify(game_name)
        if not game_path.exists():
            return []
        return sorted(path.name for path in game_path.iterdir() if path.is_dir())

    def list_presets(self, game_name: str, character_name: str) -> list[str]:
        character_path = self.root / _slugify(game_name) / _slugify(character_name or "default")
        if not character_path.exists():
            return []
        return sorted(path.stem for path in character_path.glob("*.json"))

    def copy_preset(self, game_name: str, character_name: str, preset_name: str, new_preset_name: str) -> Path:
        preset = self.load_preset(game_name, character_name, preset_name)
        preset.preset_name = new_preset_name
        return self.save_preset(preset)

    def rename_preset(self, game_name: str, character_name: str, preset_name: str, new_preset_name: str) -> Path:
        preset = self.load_preset(game_name, character_name, preset_name)
        old_path = self.preset_path(game_name, character_name, preset_name)
        preset.preset_name = new_preset_name
        new_path = self.save_preset(preset)
        if old_path.exists() and old_path != new_path:
            old_path.unlink()
        return new_path

    def delete_preset(self, game_name: str, character_name: str, preset_name: str) -> None:
        path = self.preset_path(game_name, character_name, preset_name)
        if path.exists():
            path.unlink()
