from app.controller import Controller


def test_controller_does_not_emit_events_when_stopped():
    emitted = []
    controller = Controller(
        detector=lambda frame: {"actions": {"raise_right_hand"}},
        mapper=lambda actions, preset: emitted.append((actions, preset)),
    )

    controller.process_frame(frame=None, preset=None)

    assert emitted == []


def test_controller_emits_events_when_running():
    emitted = []
    controller = Controller(
        detector=lambda frame: {"actions": {"raise_right_hand"}},
        mapper=lambda actions, preset: emitted.append((actions, preset)),
    )
    controller.start()

    result = controller.process_frame(frame="frame", preset="preset")

    assert emitted == [({"raise_right_hand"}, "preset")]
    assert result["actions"] == {"raise_right_hand"}
