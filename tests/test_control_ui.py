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
