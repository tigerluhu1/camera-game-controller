from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EditorState:
    current_game: str = ""
    current_character: str = "default"
    current_preset: str = ""
    bindings: dict[str, dict] = field(default_factory=dict)
    _saved_bindings: dict[str, dict] = field(default_factory=dict)
    is_dirty: bool = False

    def set_binding_value(self, action_name: str, input_value: str) -> None:
        binding = self.bindings.setdefault(action_name, {})
        binding["input_value"] = input_value
        self.is_dirty = True

    def load_preset(
        self,
        game_name: str,
        character_name: str,
        preset_name: str,
        bindings: dict[str, dict],
    ) -> None:
        self.current_game = game_name
        self.current_character = character_name or "default"
        self.current_preset = preset_name
        self.bindings = {action_name: dict(value) for action_name, value in bindings.items()}
        self._saved_bindings = {action_name: dict(value) for action_name, value in bindings.items()}
        self.is_dirty = False

    def discard_changes(self) -> None:
        self.bindings = {
            action_name: dict(value) for action_name, value in self._saved_bindings.items()
        }
        self.is_dirty = False
