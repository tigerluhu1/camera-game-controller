from __future__ import annotations

from typing import Callable

from app.profile_models import Preset


Sender = Callable[[str, object, str], None]


class DirectInputSender:
    def __init__(self, backend=None):
        self.backend = backend or self._load_backend()

    @staticmethod
    def _load_backend():
        try:
            import pydirectinput
        except ImportError:
            return None
        return pydirectinput

    def __call__(self, event_type: str, value: object, mode: str) -> None:
        if self.backend is None:
            return
        if event_type == "key" and mode == "tap":
            self.backend.press(str(value))
            return
        if event_type != "mouse":
            return
        if mode == "move" and isinstance(value, tuple):
            self.backend.moveRel(int(value[0]), int(value[1]), relative=True)
            return
        if mode == "tap" and value == "left_click":
            self.backend.click(button="left")
            return
        if mode == "tap" and value == "right_click":
            self.backend.click(button="right")


class InputMapper:
    def __init__(self, sender: Sender):
        self.sender = sender

    def apply_actions(self, actions: set[str], preset: Preset) -> None:
        for action_name in sorted(actions):
            binding = preset.bindings.get(action_name)
            if binding is None or not binding.enabled:
                continue
            event_type = "mouse" if binding.input_type == "mouse" else "key"
            mode = "tap"
            if binding.input_type == "mouse" and binding.input_value == "move":
                mode = "move"
            elif binding.trigger_mode:
                mode = binding.trigger_mode
            self.sender(event_type, binding.input_value, mode)

    def apply_mouse_delta(self, delta: tuple[int, int], preset: Preset) -> None:
        binding = preset.bindings.get("mouse_move")
        if binding is None or not binding.enabled or binding.input_type != "mouse":
            return
        self.sender("mouse", delta, "move")
