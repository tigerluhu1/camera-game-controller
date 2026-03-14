from app.config import AppConfig
from app.main import create_app
from app.profile_models import Preset
from app.ui import SUPPORTED_ACTIONS, build_editor_rows


def test_build_editor_rows_contains_supported_actions():
    rows = build_editor_rows()

    assert "raise_right_hand" in rows
    assert set(rows) == set(SUPPORTED_ACTIONS)


def test_new_preset_resets_editor_fields(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("old")
    app.row_vars["raise_right_hand"]["input_value"].set("1")

    app.new_preset("fresh")

    assert app.preset_var.get() == "fresh"
    assert app.row_vars["raise_right_hand"]["input_value"].get() == ""
    app.root.destroy()


def test_copy_preset_creates_new_file(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("pve")
    app.row_vars["raise_right_hand"]["input_value"].set("1")
    app.save_preset()

    app.copy_preset("raid")

    copied = app.store.load_preset("wow", "mage", "raid")
    assert copied.bindings["raise_right_hand"].input_value == "1"
    app.root.destroy()


def test_rename_preset_updates_selection_and_file_contents(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.store.save_preset(Preset(game_name="wow", character_name="mage", preset_name="pve"))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("pve")

    app.rename_preset("mythic")

    renamed = app.store.load_preset("wow", "mage", "mythic")
    assert app.preset_var.get() == "mythic"
    assert renamed.preset_name == "mythic"
    app.root.destroy()


def test_delete_preset_removes_file_and_clears_current_selection(tmp_path):
    app = create_app(AppConfig(base_dir=tmp_path))
    app.store.save_preset(Preset(game_name="wow", character_name="mage", preset_name="pve"))
    app.game_var.set("wow")
    app.character_var.set("mage")
    app.preset_var.set("pve")

    app.delete_preset(confirm=True)

    assert app.store.list_presets("wow", "mage") == []
    assert app.preset_var.get() == ""
    app.root.destroy()
