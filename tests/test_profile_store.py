from pathlib import Path

from app.profile_models import Preset
from app.profile_store import ProfileStore


def test_save_preset_writes_nested_path(tmp_path: Path):
    store = ProfileStore(tmp_path)
    preset = Preset(game_name="wow", character_name="mage", preset_name="pve")

    path = store.save_preset(preset)

    assert path == tmp_path / "wow" / "mage" / "pve.json"


def test_list_presets_returns_sorted_names(tmp_path: Path):
    store = ProfileStore(tmp_path)
    store.save_preset(Preset(game_name="wow", character_name="mage", preset_name="raid"))
    store.save_preset(Preset(game_name="wow", character_name="mage", preset_name="pve"))

    presets = store.list_presets("wow", "mage")

    assert presets == ["pve", "raid"]


def test_copy_and_rename_and_delete_preset(tmp_path: Path):
    store = ProfileStore(tmp_path)
    store.save_preset(Preset(game_name="wow", character_name="mage", preset_name="pve"))

    copied_path = store.copy_preset("wow", "mage", "pve", "raid")
    renamed_path = store.rename_preset("wow", "mage", "raid", "mythic")
    store.delete_preset("wow", "mage", "mythic")

    assert copied_path == tmp_path / "wow" / "mage" / "raid.json"
    assert renamed_path == tmp_path / "wow" / "mage" / "mythic.json"
    assert not renamed_path.exists()


def test_store_saves_and_loads_runtime_overrides(tmp_path: Path):
    store = ProfileStore(tmp_path)
    preset = Preset(
        game_name="wow",
        character_name="mage",
        preset_name="pve",
        runtime_overrides={"mouse_sensitivity": 2.2, "camera_device": 1},
    )

    store.save_preset(preset)
    loaded = store.load_preset("wow", "mage", "pve")

    assert loaded.runtime_overrides == {"mouse_sensitivity": 2.2, "camera_device": 1}
