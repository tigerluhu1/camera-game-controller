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
    def __init__(
        self,
        sender: Sender,
        mouse_sensitivity: float = 1.0,
        mouse_deadzone: int = 0,
        mouse_smoothing: float = 0.0,
    ):
        self.sender = sender
        self.mouse_sensitivity = mouse_sensitivity
        self.mouse_deadzone = mouse_deadzone
        self.mouse_smoothing = mouse_smoothing
        self._last_mouse_delta = (0.0, 0.0)

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
        if abs(delta[0]) < self.mouse_deadzone and abs(delta[1]) < self.mouse_deadzone:
            return
        scaled = (
            delta[0] * self.mouse_sensitivity,
            delta[1] * self.mouse_sensitivity,
        )
        smoothed = (
            self._last_mouse_delta[0] * self.mouse_smoothing + scaled[0] * (1 - self.mouse_smoothing),
            self._last_mouse_delta[1] * self.mouse_smoothing + scaled[1] * (1 - self.mouse_smoothing),
        )
        self._last_mouse_delta = smoothed
        rounded = (int(round(smoothed[0])), int(round(smoothed[1])))
        self.sender("mouse", rounded, "move")
