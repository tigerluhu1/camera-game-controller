from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.config import AppConfig
from app.editor_state import EditorState
from app.profile_store import ProfileStore
from app.ui import SUPPORTED_ACTIONS


class ProfileEditorApp:
    def __init__(self, config: AppConfig):
        self.config = config
        self.store = ProfileStore(config.profiles_dir)
        self.state = EditorState()
        self.root = tk.Tk()
        self.root.title("Camera Game Controller")
        self.root.geometry("820x520")
        self._build_shell()

    def _build_shell(self) -> None:
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

        ttk.Button(toolbar, text="Load", command=self.load_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Save", command=self.save_preset).pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, padding=(12, 4)).pack(fill="x")

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

    def save_preset(self) -> None:
        from app.profile_models import Binding, Preset

        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("Game and preset are required.")
            return

        bindings = {}
        for action_name, row in self.row_vars.items():
            bindings[action_name] = Binding(
                action_name=action_name,
                input_value=row["input_value"].get().strip(),
                trigger_mode=row["trigger_mode"].get().strip() or "tap",
                cooldown_ms=int(row["cooldown_ms"].get().strip() or "0"),
                enabled=bool(row["enabled"].get()),
            )

        preset = Preset(
            game_name=game_name,
            character_name=character_name,
            preset_name=preset_name,
            bindings=bindings,
        )
        self.store.save_preset(preset)
        self.state.load_preset(game_name, character_name, preset_name, preset.to_dict()["bindings"])
        self.status_var.set(f"Saved {preset_name}.")

    def run(self) -> None:
        self.root.mainloop()


def create_app(config: AppConfig | None = None) -> ProfileEditorApp:
    return ProfileEditorApp(config or AppConfig())


if __name__ == "__main__":
    create_app().run()
