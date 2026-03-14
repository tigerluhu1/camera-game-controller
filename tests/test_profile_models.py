from app.profile_models import Binding, Preset


def test_preset_defaults_character_to_default():
    preset = Preset(game_name="wow", preset_name="pve")
    assert preset.character_name == "default"


def test_preset_serializes_bindings():
    preset = Preset(
        game_name="wow",
        character_name="mage",
        preset_name="pve",
        bindings={"raise_right_hand": Binding(action_name="raise_right_hand", input_value="1")},
    )

    data = preset.to_dict()

    assert data["bindings"]["raise_right_hand"]["input_value"] == "1"


def test_preset_serializes_runtime_overrides():
    preset = Preset(
        game_name="wow",
        character_name="mage",
        preset_name="pve",
        runtime_overrides={
            "mouse_sensitivity": 1.8,
            "mouse_deadzone": 12,
        },
    )

    data = preset.to_dict()
    restored = Preset.from_dict(data)

    assert data["runtime_overrides"]["mouse_sensitivity"] == 1.8
    assert restored.runtime_overrides["mouse_deadzone"] == 12
