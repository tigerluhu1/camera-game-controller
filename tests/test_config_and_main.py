from pathlib import Path

from app.config import AppConfig
from app.main import create_app


def test_app_config_uses_profiles_dir(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)

    assert config.profiles_dir == tmp_path / "profiles"


def test_create_app_returns_shell_without_starting_mainloop(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)

    app = create_app(config)

    assert app.store.root == tmp_path / "profiles"
