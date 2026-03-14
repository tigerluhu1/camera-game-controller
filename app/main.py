from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from tkinter import TclError
from PIL import ImageTk

from app.config import AppConfig
from app.body_mouse_mapper import BodyMouseMapper
from app.camera import Camera
from app.controller import Controller
from app.detection import detect_actions
from app.editor_state import EditorState
from app.input_mapper import DirectInputSender, InputMapper
from app.preview import render_preview_frame
from app.profile_store import ProfileStore
from app.runtime_settings import RuntimeSettingsStore, resolve_runtime_settings
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
        self.runtime_store = RuntimeSettingsStore(config.settings_dir)
        self.state = EditorState()
        self.last_frame = None
        self.last_events: list[tuple[str, object, str]] = []
        self.camera = Camera()
        self.preview_status = "No preview"
        self.preview_image = None
        self.preview_photo = None
        self._last_tick_time: float | None = None
        self.direct_input_sender = DirectInputSender()
        self.vision_backend = MediaPipeVisionBackend()
        self.input_mapper = InputMapper(sender=self._dispatch_output_event)
        self.controller = Controller(detector=self._detect_frame, mapper=self._apply_actions)
        self.runtime_defaults = self.runtime_store.load()
        self.current_runtime_overrides: dict[str, float | int] = {}
        self.body_mouse_mapper = BodyMouseMapper(anchor=self.runtime_defaults.get("mouse_anchor", BodyMouseMapper.SHOULDERS))
        self._anchor_display_map = {
            BodyMouseMapper.SHOULDERS: "肩膀中心",
            BodyMouseMapper.HEAD: "头部中心",
        }
        self._display_to_anchor = {display: anchor for anchor, display in self._anchor_display_map.items()}
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
            self.status_var = SimpleVar("准备就绪")
            self.camera_status_var = SimpleVar("摄像头空闲")
            self.actions_var = SimpleVar("")
            self.event_log_var = SimpleVar("")
            self.fps_var = SimpleVar("帧率: --")
            self.runtime_source_var = SimpleVar("全局")
            self.mouse_sensitivity_var = SimpleVar(1.0)
            self.mouse_deadzone_var = SimpleVar(0)
            self.mouse_smoothing_var = SimpleVar(0.0)
            self.camera_device_var = SimpleVar(0)
            self.mouse_anchor_var = SimpleVar(BodyMouseMapper.SHOULDERS)
            self.row_vars = {}
            for action_name in SUPPORTED_ACTIONS:
                self.row_vars[action_name] = {
                    "enabled": SimpleVar(True),
                    "input_value": SimpleVar(""),
                    "trigger_mode": SimpleVar("tap"),
                    "cooldown_ms": SimpleVar("0"),
                }
            self._load_runtime_into_vars(self.runtime_defaults, source_label="全局")
            return

        toolbar = ttk.Frame(self.root, padding=12)
        toolbar.pack(fill="x")

        self.game_var = tk.StringVar()
        self.character_var = tk.StringVar(value="default")
        self.preset_var = tk.StringVar()

        for label, variable in (
            ("游戏", self.game_var),
            ("角色", self.character_var),
            ("预设", self.preset_var),
        ):
            ttk.Label(toolbar, text=label).pack(side="left", padx=(0, 6))
            ttk.Entry(toolbar, textvariable=variable, width=18).pack(side="left", padx=(0, 12))

        ttk.Button(toolbar, text="新建", command=self.prompt_new_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="复制", command=self.prompt_copy_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="重命名", command=self.prompt_rename_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="删除", command=self.prompt_delete_preset).pack(side="left", padx=(0, 12))
        ttk.Button(toolbar, text="加载", command=self.load_preset).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="保存", command=self.save_preset).pack(side="left")
        ttk.Button(toolbar, text="开始控制", command=self.start_control).pack(side="left", padx=(12, 6))
        ttk.Button(toolbar, text="停止控制", command=self.stop_control).pack(side="left")

        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(self.root, textvariable=self.status_var, padding=(12, 4)).pack(fill="x")
        self.camera_status_var = tk.StringVar(value="摄像头空闲")
        ttk.Label(self.root, textvariable=self.camera_status_var, padding=(12, 0)).pack(fill="x")
        self.actions_var = tk.StringVar(value="")
        ttk.Label(self.root, textvariable=self.actions_var, padding=(12, 0)).pack(fill="x")
        self.event_log_var = tk.StringVar(value="")
        ttk.Label(self.root, textvariable=self.event_log_var, padding=(12, 0)).pack(fill="x")
        self.fps_var = tk.StringVar(value="帧率: --")
        ttk.Label(self.root, textvariable=self.fps_var, padding=(12, 0)).pack(fill="x")
        self.runtime_source_var = tk.StringVar(value="全局")
        ttk.Label(self.root, textvariable=self.runtime_source_var, padding=(12, 0)).pack(fill="x")

        content = ttk.Frame(self.root, padding=12)
        content.pack(fill="both", expand=True)

        table = ttk.Frame(content)
        table.pack(side="left", fill="both", expand=True)

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

        preview_panel = ttk.Frame(content, padding=(12, 0))
        preview_panel.pack(side="right", fill="y")
        ttk.Label(preview_panel, text="摄像头预览").pack(anchor="w")
        self.camera_device_var = tk.IntVar(value=self.camera.device_index)
        self.mouse_sensitivity_var = tk.DoubleVar(value=self.input_mapper.mouse_sensitivity)
        self.mouse_deadzone_var = tk.IntVar(value=self.input_mapper.mouse_deadzone)
        self.mouse_smoothing_var = tk.DoubleVar(value=self.input_mapper.mouse_smoothing)
        self.mouse_anchor_var = tk.StringVar(value=self.runtime_defaults.get("mouse_anchor", BodyMouseMapper.SHOULDERS))
        self.mouse_anchor_display_var = tk.StringVar(
            value=self._anchor_display_map.get(
                self.mouse_anchor_var.get(), self._anchor_display_map[BodyMouseMapper.SHOULDERS]
            )
        )
        ttk.Label(preview_panel, text="摄像头设备").pack(anchor="w", pady=(8, 0))
        ttk.Spinbox(preview_panel, from_=0, to=5, textvariable=self.camera_device_var, width=8).pack(anchor="w")
        ttk.Label(preview_panel, text="鼠标灵敏度").pack(anchor="w", pady=(8, 0))
        ttk.Scale(preview_panel, from_=0.1, to=5.0, variable=self.mouse_sensitivity_var, orient="horizontal").pack(anchor="w", fill="x")
        ttk.Label(preview_panel, text="鼠标死区").pack(anchor="w", pady=(8, 0))
        ttk.Spinbox(preview_panel, from_=0, to=100, textvariable=self.mouse_deadzone_var, width=8).pack(anchor="w")
        ttk.Label(preview_panel, text="鼠标平滑").pack(anchor="w", pady=(8, 0))
        ttk.Scale(preview_panel, from_=0.0, to=0.95, variable=self.mouse_smoothing_var, orient="horizontal").pack(anchor="w", fill="x")
        ttk.Label(preview_panel, text="鼠标锚点").pack(anchor="w", pady=(8, 0))
        anchor_box = ttk.Combobox(
            preview_panel,
            textvariable=self.mouse_anchor_display_var,
            values=list(self._anchor_display_map.values()),
            state="readonly",
            width=12,
        )
        anchor_box.pack(anchor="w")
        anchor_box.bind("<<ComboboxSelected>>", self._on_anchor_display_changed)
        ttk.Button(preview_panel, text="保存运行默认值", command=self.save_runtime_defaults).pack(anchor="w", pady=(8, 0), fill="x")
        ttk.Button(preview_panel, text="保存到当前预设", command=self.save_runtime_to_preset).pack(anchor="w", pady=(4, 0), fill="x")
        ttk.Button(preview_panel, text="重置为默认", command=self.reset_runtime_to_defaults).pack(anchor="w", pady=(4, 0), fill="x")
        self.preview_label = ttk.Label(preview_panel, text="暂无预览", width=40)
        self.preview_label.pack(anchor="w", pady=(8, 0))
        self._load_runtime_into_vars(self.runtime_defaults, source_label="全局")

    def _current_runtime_values(self) -> dict[str, float | int]:
        return {
            "mouse_sensitivity": float(self.mouse_sensitivity_var.get()),
            "mouse_deadzone": int(self.mouse_deadzone_var.get()),
            "mouse_smoothing": float(self.mouse_smoothing_var.get()),
            "camera_device": int(self.camera_device_var.get()),
            "mouse_anchor": str(self.mouse_anchor_var.get()),
        }

    def _load_runtime_into_vars(self, values: dict[str, float | int], source_label: str) -> None:
        self.mouse_sensitivity_var.set(float(values["mouse_sensitivity"]))
        self.mouse_deadzone_var.set(int(values["mouse_deadzone"]))
        self.mouse_smoothing_var.set(float(values["mouse_smoothing"]))
        self.camera_device_var.set(int(values["camera_device"]))
        self.mouse_anchor_var.set(str(values.get("mouse_anchor", BodyMouseMapper.SHOULDERS)))
        if hasattr(self, "mouse_anchor_display_var"):
            display = self._anchor_display_map.get(
                self.mouse_anchor_var.get(), self._anchor_display_map[BodyMouseMapper.SHOULDERS]
            )
            self.mouse_anchor_display_var.set(display)
        self.runtime_source_var.set(source_label)
        self.apply_runtime_settings()

    def _resolved_runtime_settings(self, preset_overrides: dict[str, float | int] | None = None) -> dict[str, float | int]:
        return resolve_runtime_settings(self.runtime_defaults, preset_overrides or self.current_runtime_overrides)

    def _on_anchor_display_changed(self, *_):
        if not hasattr(self, "mouse_anchor_display_var"):
            return
        display = self.mouse_anchor_display_var.get()
        anchor = self._display_to_anchor.get(display, BodyMouseMapper.SHOULDERS)
        self.mouse_anchor_var.set(anchor)
        self.body_mouse_mapper.anchor = anchor
        self.apply_runtime_settings()

    def load_preset(self) -> None:
        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("请输入游戏和预设名称进行加载。")
            return
        try:
            preset = self.store.load_preset(game_name, character_name, preset_name)
        except FileNotFoundError:
            self.status_var.set("未找到预设。")
            return
        self.state.load_preset(game_name, character_name, preset_name, preset.to_dict()["bindings"])
        for action_name in SUPPORTED_ACTIONS:
            row = self.row_vars[action_name]
            binding = preset.bindings.get(action_name)
            row["enabled"].set(binding.enabled if binding else True)
            row["input_value"].set(binding.input_value if binding else "")
            row["trigger_mode"].set(binding.trigger_mode if binding else "tap")
            row["cooldown_ms"].set(str(binding.cooldown_ms if binding else 0))
        self.current_runtime_overrides = dict(preset.runtime_overrides)
        source_label = "预设覆盖" if self.current_runtime_overrides else "全局"
        self._load_runtime_into_vars(self._resolved_runtime_settings(preset.runtime_overrides), source_label=source_label)
        self.status_var.set(f"已加载 {preset_name}。")

    def _clear_rows(self) -> None:
        for row in self.row_vars.values():
            row["enabled"].set(True)
            row["input_value"].set("")
            row["trigger_mode"].set("tap")
            row["cooldown_ms"].set("0")

    def _record_output_event(self, event_type: str, value: object, mode: str) -> None:
        self.last_events.append((event_type, value, mode))
        self.last_events = self.last_events[-10:]
        if hasattr(self, "event_log_var"):
            lines = [f"{kind}:{value}:{mode}" for kind, value, mode in self.last_events[-5:]]
            self.event_log_var.set(" | ".join(lines))

    def _dispatch_output_event(self, event_type: str, value: object, mode: str) -> None:
        self._record_output_event(event_type, value, mode)
        self.direct_input_sender(event_type, value, mode)

    def update_fps(self, fps: float) -> None:
        self.fps_var.set(f"帧率: {fps:.1f}")

    def set_camera_device(self, device_index: int) -> None:
        self.camera.device_index = int(device_index)
        if hasattr(self, "camera_device_var"):
            self.camera_device_var.set(int(device_index))

    def apply_runtime_settings(self) -> None:
        self.input_mapper.mouse_sensitivity = float(self.mouse_sensitivity_var.get())
        self.input_mapper.mouse_deadzone = int(self.mouse_deadzone_var.get())
        self.input_mapper.mouse_smoothing = float(self.mouse_smoothing_var.get())
        self.body_mouse_mapper.anchor = self.mouse_anchor_var.get()
        self.set_camera_device(int(self.camera_device_var.get()))

    def _current_preset(self):
        preset_name = self.preset_var.get().strip()
        game_name = self.game_var.get().strip()
        if not game_name or not preset_name:
            return None
        return self._build_preset_from_rows()

    def _detect_frame(self, frame) -> dict:
        vision_result = self.vision_backend.process_frame(frame)
        actions = detect_actions(vision_result.landmarks, vision_result.hand_states)
        return {
            "actions": actions,
            "landmarks": vision_result.landmarks,
            "hand_states": vision_result.hand_states,
        }

    def _apply_actions(self, actions: set[str], preset) -> None:
        if preset is None:
            return
        self.input_mapper.apply_actions(actions, preset)
        self.actions_var.set(", ".join(sorted(actions)))

    def _apply_body_mouse_movement(self, landmarks: dict, frame, preset) -> None:
        if not self.controller.status.running or preset is None:
            return
        size = self._frame_size(frame)
        if size is None:
            return
        delta = self.body_mouse_mapper.compute_mouse_delta(landmarks or {}, size)
        if delta == (0, 0):
            return
        self.input_mapper.apply_mouse_delta(delta, preset)

    def _frame_size(self, frame) -> tuple[int, int] | None:
        if frame is None:
            return None
        shape = getattr(frame, "shape", None)
        if not shape or len(shape) < 2:
            return None
        return (shape[1], shape[0])

    def process_current_frame(self):
        self.apply_runtime_settings()
        frame = self.camera.read()
        if frame is None:
            self.camera_status_var.set("未获取到摄像头画面")
            return {"actions": set(), "running": self.controller.status.running}
        self.last_frame = frame
        preset = self._current_preset()
        result = self.controller.process_frame(frame, preset)
        self.actions_var.set(", ".join(sorted(result["actions"])))
        if result["running"]:
            self._apply_body_mouse_movement(result.get("landmarks", {}), frame, preset)
        self.preview_image = render_preview_frame(
            frame,
            result.get("landmarks", {}),
            result["actions"],
        )
        self.preview_status = "预览已更新"
        if not self._headless and self.preview_image is not None:
            try:
                self.preview_photo = ImageTk.PhotoImage(self.preview_image)
                self.preview_label.configure(image=self.preview_photo, text="")
            except TclError:
                self.preview_photo = None
                self.preview_label.configure(text="预览已更新")
        now = time.perf_counter()
        if self._last_tick_time is not None:
            elapsed = now - self._last_tick_time
            if elapsed > 0:
                self.update_fps(1.0 / elapsed)
        self._last_tick_time = now
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
            runtime_overrides=dict(self.current_runtime_overrides),
        )

    def save_runtime_defaults(self) -> None:
        self.runtime_defaults = self._current_runtime_values()
        self.runtime_store.save(self.runtime_defaults)
        if not self.current_runtime_overrides:
            self._load_runtime_into_vars(self.runtime_defaults, source_label="全局")
        else:
            self.runtime_source_var.set("预设覆盖")
            self.apply_runtime_settings()
        self.status_var.set("运行参数默认设置已保存。")

    def save_runtime_to_preset(self) -> None:
        if not self.game_var.get().strip() or not self.preset_var.get().strip():
            self.status_var.set("游戏和预设是必填项。")
            return
        current = self._current_runtime_values()
        overrides = {
            key: value
            for key, value in current.items()
            if self.runtime_defaults.get(key) != value
        }
        self.current_runtime_overrides = overrides
        self.runtime_source_var.set("预设覆盖" if overrides else "全局")
        self.apply_runtime_settings()
        self.status_var.set("运行设置已关联到预设。")

    def reset_runtime_to_defaults(self) -> None:
        self.current_runtime_overrides = {}
        game_name = self.game_var.get().strip()
        preset_name = self.preset_var.get().strip()
        if game_name and preset_name:
            preset = self._build_preset_from_rows()
            preset.runtime_overrides = {}
            self.store.save_preset(preset)
        self._load_runtime_into_vars(self.runtime_defaults, source_label="全局")
        self.status_var.set("运行参数已重置为默认。")

    def save_preset(self) -> None:
        game_name = self.game_var.get().strip()
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("游戏和预设是必填项。")
            return

        preset = self._build_preset_from_rows()
        self.store.save_preset(preset)
        self.state.load_preset(game_name, preset.character_name, preset_name, preset.to_dict()["bindings"])
        self.status_var.set(f"已保存 {preset_name}。")

    def new_preset(self, preset_name: str) -> None:
        self.preset_var.set(preset_name)
        self._clear_rows()
        self.current_runtime_overrides = {}
        self._load_runtime_into_vars(self.runtime_defaults, source_label="全局")
        self.state.load_preset(
            self.game_var.get().strip(),
            self.character_var.get().strip() or "default",
            preset_name,
            {},
        )
        self.status_var.set(f"新预设 {preset_name} 已就绪。")

    def copy_preset(self, new_preset_name: str) -> None:
        preset = self._build_preset_from_rows(new_preset_name)
        self.store.save_preset(preset)
        self.preset_var.set(new_preset_name)
        self.state.load_preset(preset.game_name, preset.character_name, new_preset_name, preset.to_dict()["bindings"])
        self.status_var.set(f"已复制为 {new_preset_name}。")

    def rename_preset(self, new_preset_name: str) -> None:
        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("请先加载预设再重命名。")
            return
        self.store.rename_preset(game_name, character_name, preset_name, new_preset_name)
        self.preset_var.set(new_preset_name)
        loaded = self.store.load_preset(game_name, character_name, new_preset_name)
        self.state.load_preset(game_name, character_name, new_preset_name, loaded.to_dict()["bindings"])
        self.status_var.set(f"已重命名为 {new_preset_name}。")

    def delete_preset(self, confirm: bool = False) -> None:
        game_name = self.game_var.get().strip()
        character_name = self.character_var.get().strip() or "default"
        preset_name = self.preset_var.get().strip()
        if not game_name or not preset_name:
            self.status_var.set("请先加载预设再删除。")
            return
        if not confirm:
            confirm = messagebox.askyesno("删除预设", f"确定要删除预设「{preset_name}」吗？")
        if not confirm:
            self.status_var.set("已取消删除。")
            return
        self.store.delete_preset(game_name, character_name, preset_name)
        self.preset_var.set("")
        self._clear_rows()
        self.current_runtime_overrides = {}
        self._load_runtime_into_vars(self.runtime_defaults, source_label="全局")
        self.state.load_preset(game_name, character_name, "", {})
        self.status_var.set(f"已删除 {preset_name}。")

    def prompt_new_preset(self) -> None:
        if self._headless:
            return
        preset_name = simpledialog.askstring("新建预设", "预设名称：", parent=self.root)
        if preset_name:
            self.new_preset(preset_name)

    def prompt_copy_preset(self) -> None:
        if self._headless:
            return
        preset_name = simpledialog.askstring("复制预设", "新预设名称：", parent=self.root)
        if preset_name:
            self.copy_preset(preset_name)

    def prompt_rename_preset(self) -> None:
        if self._headless:
            return
        preset_name = simpledialog.askstring("重命名预设", "新预设名称：", parent=self.root)
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
            self.camera_status_var.set("控制已启动")
            self.control_tick()
        else:
            self.controller.stop()
            self.camera_status_var.set(status.last_error or "摄像头启动失败")

    def stop_control(self) -> None:
        self.controller.stop()
        self.camera.close()
        self.camera_status_var.set("控制已停止")

    def run(self) -> None:
        self.root.mainloop()


def create_app(config: AppConfig | None = None) -> ProfileEditorApp:
    return ProfileEditorApp(config or AppConfig())


if __name__ == "__main__":
    create_app().run()
