from app.config import AppConfig
from app.detection import LandmarkPoint
from app.main import create_app
import numpy as np


def test_app_has_control_buttons_and_status(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))

    assert hasattr(app, "start_control")
    assert hasattr(app, "stop_control")
    assert hasattr(app, "controller")
    app.root.destroy()


def test_start_and_stop_control_toggle_status(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))

    class FakeCamera:
        def open(self):
            return type("Status", (), {"running": True, "last_error": "", "frame_size": (640, 480)})()

        def read(self):
            return None

        def close(self):
            return None

    app.camera = FakeCamera()

    app.start_control()
    assert app.controller.status.running is True

    app.stop_control()
    assert app.controller.status.running is False
    app.root.destroy()


def test_process_current_frame_updates_actions_and_events(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("pve")
    app.row_vars["raise_right_hand"]["input_value"].set("1")

    class FakeCamera:
        def open(self):
            return type("Status", (), {"running": True, "last_error": "", "frame_size": (640, 480)})()

        def read(self):
            return np.zeros((24, 32, 3), dtype="uint8")

        def close(self):
            return None

    app.camera = FakeCamera()
    app._detect_frame = lambda frame: {"actions": {"raise_right_hand"}}
    app.controller.detector = app._detect_frame
    app.start_control()

    result = app.process_current_frame()

    assert result["actions"] == {"raise_right_hand"}
    assert app.actions_var.get() == "raise_right_hand"
    assert app.last_events[-1] == ("key", "1", "tap")
    assert app.preview_status == "Preview updated"
    assert app.preview_image is not None
    app.root.destroy()


def test_start_control_does_not_run_when_camera_fails(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))

    class FakeCamera:
        def open(self):
            return type("Status", (), {"running": False, "last_error": "Camera backend unavailable"})()

        def close(self):
            return None

    app.camera = FakeCamera()
    app.start_control()

    assert app.controller.status.running is False
    assert app.camera_status_var.get() == "Camera backend unavailable"
    app.root.destroy()


def test_start_control_processes_first_frame_when_camera_starts(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    calls = []

    class FakeCamera:
        def open(self):
            return type("Status", (), {"running": True, "last_error": "", "frame_size": (640, 480)})()

        def read(self):
            calls.append("read")
            return None

        def close(self):
            return None

    app.camera = FakeCamera()
    app.start_control()

    assert "read" in calls
    app.root.destroy()


def test_switch_camera_device_updates_camera_index(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))

    app.set_camera_device(2)

    assert app.camera.device_index == 2
    app.root.destroy()


def test_event_log_and_fps_status_update(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app._record_output_event("key", "1", "tap")
    app.update_fps(27.5)

    assert "key:1:tap" in app.event_log_var.get()
    assert "27.5" in app.fps_var.get()
    app.root.destroy()


def test_runtime_defaults_and_overrides_round_trip_through_ui(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("pve")

    app.mouse_sensitivity_var.set(1.9)
    app.mouse_deadzone_var.set(11)
    app.mouse_smoothing_var.set(0.45)
    app.camera_device_var.set(2)
    app.save_runtime_defaults()

    app.mouse_sensitivity_var.set(2.7)
    app.camera_device_var.set(4)
    app.save_runtime_to_preset()
    app.save_preset()

    app.mouse_sensitivity_var.set(0.5)
    app.mouse_deadzone_var.set(1)
    app.mouse_smoothing_var.set(0.1)
    app.camera_device_var.set(0)
    app.load_preset()

    assert app.mouse_sensitivity_var.get() == 2.7
    assert app.mouse_deadzone_var.get() == 11
    assert app.mouse_smoothing_var.get() == 0.45
    assert app.camera_device_var.get() == 4
    assert app.runtime_source_var.get() == "Preset Override"
    app.root.destroy()


def test_reset_runtime_to_defaults_clears_preset_override(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("pve")
    app.mouse_sensitivity_var.set(1.5)
    app.mouse_deadzone_var.set(8)
    app.mouse_smoothing_var.set(0.3)
    app.camera_device_var.set(1)
    app.save_runtime_defaults()

    app.mouse_sensitivity_var.set(2.5)
    app.save_runtime_to_preset()
    app.save_preset()

    app.reset_runtime_to_defaults()

    assert app.mouse_sensitivity_var.get() == 1.5
    assert app.runtime_source_var.get() == "Global"
    loaded = app.store.load_preset("wow", "mage", "pve")
    assert loaded.runtime_overrides == {}
    app.root.destroy()


def test_runtime_anchor_default_and_persistence(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    assert app.mouse_anchor_var.get() == "shoulders"
    app.mouse_anchor_var.set("head")
    app.save_runtime_defaults()

    reopened = create_app(AppConfig(base_dir=tmp_path))

    assert reopened.mouse_anchor_var.get() == "head"
    reopened.root.destroy()
    app.root.destroy()


def test_body_anchor_triggers_mouse_delta(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("pve")
    app.save_preset()

    class FakeCamera:
        def open(self):
            return type("Status", (), {"running": True, "last_error": "", "frame_size": (640, 480)})()

        def read(self):
            import numpy as np

            return np.zeros((24, 32, 3), dtype="uint8")

        def close(self):
            return None

    app.camera = FakeCamera()
    app._detect_frame = lambda frame: {
        "actions": set(),
        "landmarks": {
            "left_shoulder": LandmarkPoint(x=0.2, y=0.5),
            "right_shoulder": LandmarkPoint(x=0.4, y=0.5),
        },
    }
    app.controller.detector = app._detect_frame

    deltas = []
    app.input_mapper.apply_mouse_delta = lambda delta, preset: deltas.append(delta)

    app.controller.start()
    app.process_current_frame()

    assert deltas
    dx, _ = deltas[0]
    assert dx < 0
    app.root.destroy()
