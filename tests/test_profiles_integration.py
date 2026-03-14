from pathlib import Path

from app.profiles import list_available_presets


def test_list_available_presets_groups_by_game_and_character(tmp_path: Path):
    (tmp_path / "wow" / "mage").mkdir(parents=True)
    (tmp_path / "wow" / "mage" / "pve.json").write_text("{}", encoding="utf-8")

    tree = list_available_presets(tmp_path)

    assert tree["wow"]["mage"] == ["pve"]
