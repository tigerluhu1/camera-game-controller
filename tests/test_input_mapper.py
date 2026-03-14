from app.input_mapper import InputMapper
from app.profile_models import Binding, Preset


def test_mapper_emits_keyboard_and_mouse_commands():
    events = []

    def sender(event_type, value, mode):
        events.append((event_type, value, mode))

    preset = Preset(
        game_name="wow",
        preset_name="pve",
        bindings={
            "raise_right_hand": Binding(action_name="raise_right_hand", input_value="1"),
            "right_fist": Binding(
                action_name="right_fist",
                input_type="mouse",
                input_value="left_click",
            ),
        },
    )

    mapper = InputMapper(sender=sender)
    mapper.apply_actions({"raise_right_hand", "right_fist"}, preset)

    assert ("key", "1", "tap") in events
    assert ("mouse", "left_click", "tap") in events


def test_mapper_emits_relative_mouse_move():
    events = []

    def sender(event_type, value, mode):
        events.append((event_type, value, mode))

    preset = Preset(
        game_name="wow",
        preset_name="pve",
        bindings={
            "mouse_move": Binding(
                action_name="mouse_move",
                input_type="mouse",
                input_value="move",
            ),
        },
    )

    mapper = InputMapper(sender=sender)
    mapper.apply_mouse_delta((12, -6), preset)

    assert events == [("mouse", (12, -6), "move")]
