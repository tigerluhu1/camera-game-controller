from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter import TclError

from app.config import AppConfig
from app.camera import Camera
from app.controller import Controller
from app.detection import detect_actions
from app.editor_state import EditorState
from app.input_mapper import DirectInputSender, InputMapper
from app.profile_store import ProfileStore
from app.ui import SUPPORTED_ACTIONS
from app.vision_backend import MediaPipeVisionBackend


class SimpleVar:
    def __init__(self, value=None):
        self._value = value

    def get(self):
        return self._value

    def set(self, value) -> None:
        self._value = value


class HeadlessRoot:
    def title(self, _value: str) -> None:
        return None

    def geometry(self, _value: str) -> None:
        return None

    def destroy(self) -> None:
        return None

    def mainloop(self) -> None:
        return None

    def after(self, _delay_ms: int, callback) -> None:
        callback()


class ProfileEditorApp:
    def __init__(self, config: AppConfig):
        self.config = config
        self.store = ProfileStore(config.profiles_dir)
        self.state = EditorState()
        self.last_frame = None
        self.last_events: list[tuple[str, object, str]] = []
        self.camera = Camera()
        self.preview_status = "No preview"
        self.direct_input_sender = DirectInputSender()
        self.vision_backend = MediaPipeVisionBackend()
        self.input_mapper = InputMapper(sender=self._dispatch_output_event)
        self.controller = Controller(detector=self._detect_frame, mapper=self._apply_actions)
        self._headless = False
        try:
            self.root = tk.Tk()
        except TclError:
            self.root = HeadlessRoot()
            self._headless = True
        self.root.title("Camera Game Controller")
        self.root.geometry("820x520")
        self._build_shell()

    def _build_shell(self) -> None:
        if self._headless:
            self.game_var = SimpleVar("")
            self.character_var = SimpleVar("default")
            self.preset_var = SimpleVar("")
            self.status_var = SimpleVar("Ready")
            self.camera_status_var = SimpleVar("Camera idle")
            self.actions_var = SimpleVar("")
            self.row_vars = {}
            for action_name in SUPPORTED_ACTIONS:
                self.row_vars[action_name] = {
                    "enabled": SimpleVar(True),
                    "input_value": SimpleVar(""),
                    "trigger_mode": SimpleVar("tap"),
                    "cooldown_ms": SimpleVar("0"),
                }
            return

        toolbar = ttk.Frame(self.root, padding=12)
        toolbar.pack(fill="x")

        self.game_var = tk.StringVar()
        self.character_var = tk.StringVar(value="default")
        self.preset_var = tk.StringVar()

        for label, variable in (
            ("Game", self.game_var),
            ("Character", self.character_var),
            ("Preset", self.preset_var),
        ):
            ttk.Label(toolbar, text=label).pack(side="left", padx=(0, 6))
            ttk.Entry(toolbar, textvariable=variable, width=18).pack(side="left", padx=(0, 12))

        ttk.Button(toolbar, text="New", command=self.prompt_new_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Copy", command=self.prompt_copy_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Rename", command=self.prompt_rename_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Delete", command=self.prompt_delete_preset).pack(side="left", padx=(0, 12))
        ttk.Button(toolbar, text="Load", command=self.load_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Save", command=self.save_preset).pack(side="left")
        ttk.Button(toolbar, text="Start Control", command=self.start_control).pack(side="left", padx=(12, 6))
        ttk.Button(toolbar, text="Stop Control", command=self.stop_control).pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, padding=(12, 4)).pack(fill="x")
        self.camera_status_var = tk.StringVar(value="Camera idle")
        ttk.Label(self.root, textvariable=self.camera_status_var, padding=(12, 0)).pack(fill="x")
        self.actions_var = tk.StringVar(value="")
        ttk.Label(self.root, textvariable=self.actions_var, padding=(12, 0)).pack(fill="x")

        table = ttk.Frame(self.root, padding=12)
        table.pack(fill="both", expand=True)

        headings = ("Action", "Enabled", "Input", "Mode", "Cooldown(ms)")
        for column, heading in enumerate(headings):
            ttk.Label(table, text=heading).grid(row=0, column=column, sticky="w", padx=4, pady=4)

        self.row_vars: dict[str, dict[str, tk.Variable]] = {}
        for row_index, action_name in enumerate(SUPPORTED_ACTIONS, start=1):
            enabled_var = tk.BooleanVar(value=True)
            input_var = tk.StringVar()
            mode_var = tk.StringVar(value="tap")
            cooldown_var = tk.StringVar(value="0")
            self.row_vars[action_name] = {
                "enabled": enabled_var,
                "input_value": input_var,
                "trigger_mode": mode_var,
                "cooldown_ms": cooldown_var,
            }
            ttk.Label(table, text=action_name).grid(row=row_index, column=0, sticky="w", padx=4, pady=4)
            ttk.Checkbutton(table, variable=enabled_var).grid(row=row_index, column=1, sticky="w", padx=4)
            ttk.Entry(table, textvariable=input_var, width=10).grid(row=row_index, column=2, sticky="w", padx=4)
            ttk.Combobox(
                table,
                textvariable=mode_var,
                values=("tap", "hold"),
                width=8,
                state="readonly",
            ).grid(row=row_index, column=3, sticky="w", padx=4)
            ttk.Entry(table, textvariable=cooldown_var, width=10).grid(row=row_index, column=4, sticky="w", padx=4)

    def load_preset(self) -> None:
        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("Enter a game and preset name to load.")
            return
        try:
            preset = self.store.load_preset(game_name, character_name, preset_name)
        except FileNotFoundError:
            self.status_var.set("Preset not found.")
            return
        self.state.load_preset(game_name, character_name, preset_name, preset.to_dict()["bindings"])
        for action_name in SUPPORTED_ACTIONS:
            row = self.row_vars[action_name]
            binding = preset.bindings.get(action_name)
            row["enabled"].set(binding.enabled if binding else True)
            row["input_value"].set(binding.input_value if binding else "")
            row["trigger_mode"].set(binding.trigger_mode if binding else "tap")
            row["cooldown_ms"].set(str(binding.cooldown_ms if binding else 0))
        self.status_var.set(f"Loaded {preset_name}.")

    def _clear_rows(self) -> None:
        for row in self.row_vars.values():
            row["enabled"].set(True)
            row["input_value"].set("")
            row["trigger_mode"].set("tap")
            row["cooldown_ms"].set("0")

    def _record_output_event(self, event_type: str, value: object, mode: str) -> None:
        self.last_events.append((event_type, value, mode))
        self.last_events = self.last_events[-10:]

    def _dispatch_output_event(self, event_type: str, value: object, mode: str) -> None:
        self._record_output_event(event_type, value, mode)
        self.direct_input_sender(event_type, value, mode)

    def _current_preset(self):
        preset_name = self.preset_var.get().strip()
        game_name = self.game_var.get().strip()
        if not game_name or not preset_name:
            return None
        return self._build_preset_from_rows()

    def _detect_frame(self, frame) -> dict:
        vision_result = self.vision_backend.process_frame(frame)
        actions = detect_actions(vision_result.landmarks, vision_result.hand_states)
        return {"actions": actions}

    def _apply_actions(self, actions: set[str], preset) -> None:
        if preset is None:
            return
        self.input_mapper.apply_actions(actions, preset)
        self.actions_var.set(", ".join(sorted(actions)))

    def process_current_frame(self):
        frame = self.camera.read()
        if frame is None:
            self.camera_status_var.set("No camera frame")
            return {"actions": set(), "running": self.controller.status.running}
        self.last_frame = frame
        self.preview_status = "Preview updated"
        preset = self._current_preset()
        result = self.controller.process_frame(frame, preset)
        self.actions_var.set(", ".join(sorted(result["actions"])))
        return result

    def control_tick(self) -> None:
        if not self.controller.status.running:
            return
        self.process_current_frame()
        if not self._headless and hasattr(self.root, "after"):
            self.root.after(33, self.control_tick)

    def _build_preset_from_rows(self, preset_name: str | None = None):
        from app.profile_models import Binding, Preset

        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        resolved_preset_name = (preset_name or self.preset_var.get()).strip()
        bindings = {}
        for action_name, row in self.row_vars.items():
            bindings[action_name] = Binding(
                action_name=action_name,
                input_value=row["input_value"].get().strip(),
                trigger_mode=row["trigger_mode"].get().strip() or "tap",
                cooldown_ms=int(row["cooldown_ms"].get().strip() or "0"),
                enabled=bool(row["enabled"].get()),
            )
        return Preset(
            game_name=game_name,
            character_name=character_name,
            preset_name=resolved_preset_name,
            bindings=bindings,
        )

    def save_preset(self) -> None:
        game_name = self.game_var.get().strip()
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("Game and preset are required.")
            return

        preset = self._build_preset_from_rows()
        self.store.save_preset(preset)
        self.state.load_preset(game_name, preset.character_name, preset_name, preset.to_dict()["bindings"])
        self.status_var.set(f"Saved {preset_name}.")

    def new_preset(self, preset_name: str) -> None:
        self.preset_var.set(preset_name)
        self._clear_rows()
        self.state.load_preset(
            self.game_var.get().strip(),
            self.character_var.get().strip() or "default",
            preset_name,
            {},
        )
        self.status_var.set(f"New preset {preset_name} ready.")

    def copy_preset(self, new_preset_name: str) -> None:
        preset = self._build_preset_from_rows(new_preset_name)
        self.store.save_preset(preset)
        self.preset_var.set(new_preset_name)
        self.state.load_preset(preset.game_name, preset.character_name, new_preset_name, preset.to_dict()["bindings"])
        self.status_var.set(f"Copied to {new_preset_name}.")

    def rename_preset(self, new_preset_name: str) -> None:
        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("Load a preset before renaming.")
            return
        self.store.rename_preset(game_name, character_name, preset_name, new_preset_name)
        self.preset_var.set(new_preset_name)
        loaded = self.store.load_preset(game_name, character_name, new_preset_name)
        self.state.load_preset(game_name, character_name, new_preset_name, loaded.to_dict()["bindings"])
        self.status_var.set(f"Renamed to {new_preset_name}.")

    def delete_preset(self, confirm: bool = False) -> None:
        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("Load a preset before deleting.")
            return
        if not confirm:
            confirm = messagebox.askyesno("Delete Preset", f"Delete preset '{preset_name}'?")
        if not confirm:
            self.status_var.set("Delete cancelled.")
            return
        self.store.delete_preset(game_name, character_name, preset_name)
        self.preset_var.set("")
        self._clear_rows()
        self.state.load_preset(game_name, character_name, "", {})
        self.status_var.set(f"Deleted {preset_name}.")

    def prompt_new_preset(self) -> None:
        if self._headless:
            return
        preset_name = simpledialog.askstring("New Preset", "Preset name:", parent=self.root)
        if preset_name:
            self.new_preset(preset_name)

    def prompt_copy_preset(self) -> None:
        if self._headless:
            return
        preset_name = simpledialog.askstring("Copy Preset", "New preset name:", parent=self.root)
        if preset_name:
            self.copy_preset(preset_name)

    def prompt_rename_preset(self) -> None:
        if self._headless:
            return
        preset_name = simpledialog.askstring("Rename Preset", "New preset name:", parent=self.root)
        if preset_name:
            self.rename_preset(preset_name)

    def prompt_delete_preset(self) -> None:
        if self._headless:
            return
        self.delete_preset()

    def start_control(self) -> None:
        status = self.camera.open()
        if status.running:
            self.controller.start()
            self.camera_status_var.set("Control running")
            self.control_tick()
        else:
            self.controller.stop()
            self.camera_status_var.set(status.last_error or "Camera failed")

    def stop_control(self) -> None:
        self.controller.stop()
        self.camera.close()
        self.camera_status_var.set("Control stopped")

    def run(self) -> None:
        self.root.mainloop()


def create_app(config: AppConfig | None = None) -> ProfileEditorApp:
    return ProfileEditorApp(config or AppConfig())


if __name__ == "__main__":
    create_app().run()
