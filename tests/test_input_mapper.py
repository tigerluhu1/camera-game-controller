from app.input_mapper import DirectInputSender, InputMapper
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


def test_direct_input_sender_routes_events_to_backend():
    calls = []

    class FakeBackend:
        def press(self, key):
            calls.append(("press", key))

        def moveRel(self, x, y, relative=True):
            calls.append(("moveRel", x, y, relative))

        def click(self, button="left"):
            calls.append(("click", button))

    sender = DirectInputSender(backend=FakeBackend())
    sender("key", "1", "tap")
    sender("mouse", (10, -5), "move")
    sender("mouse", "left_click", "tap")

    assert calls == [
        ("press", "1"),
        ("moveRel", 10, -5, True),
        ("click", "left"),
    ]


def test_mapper_applies_sensitivity_deadzone_and_smoothing():
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

    mapper = InputMapper(sender=sender, mouse_sensitivity=2.0, mouse_deadzone=5, mouse_smoothing=0.5)
    mapper.apply_mouse_delta((4, 4), preset)
    mapper.apply_mouse_delta((10, 0), preset)

    assert events == [("mouse", (10, 0), "move")]
