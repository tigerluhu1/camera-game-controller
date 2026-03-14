from pathlib import Path

from app.runtime_settings import RuntimeSettingsStore, resolve_runtime_settings


def test_runtime_settings_store_reads_written_defaults(tmp_path: Path):
    store = RuntimeSettingsStore(tmp_path / "settings")
    defaults = {
        "mouse_sensitivity": 1.7,
        "mouse_deadzone": 9,
        "mouse_smoothing": 0.4,
        "camera_device": 2,
        "mouse_anchor": "shoulders",
    }

    store.save(defaults)
    loaded = store.load()

    assert loaded == defaults


def test_resolve_runtime_settings_applies_preset_overrides(tmp_path: Path):
    store = RuntimeSettingsStore(tmp_path / "settings")
    store.save(
        {
            "mouse_sensitivity": 1.4,
            "mouse_deadzone": 7,
            "mouse_smoothing": 0.2,
            "camera_device": 0,
        }
    )

    resolved = resolve_runtime_settings(
        store.load(),
        {
            "mouse_sensitivity": 2.0,
            "camera_device": 3,
        },
    )

    assert resolved == {
        "mouse_sensitivity": 2.0,
        "mouse_deadzone": 7,
        "mouse_smoothing": 0.2,
        "camera_device": 3,
        "mouse_anchor": "shoulders",
    }
