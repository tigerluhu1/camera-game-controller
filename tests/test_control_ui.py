from app.config import AppConfig
from app.main import create_app


def test_app_has_control_buttons_and_status(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))

    assert hasattr(app, "start_control")
    assert hasattr(app, "stop_control")
    assert hasattr(app, "controller")
    app.root.destroy()


def test_start_and_stop_control_toggle_status(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))

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
            return "frame"

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
    app.root.destroy()
