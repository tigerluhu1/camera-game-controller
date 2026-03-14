from app.editor_state import EditorState


def test_mark_dirty_when_binding_changes():
    state = EditorState()

    state.set_binding_value("raise_right_hand", "1")

    assert state.is_dirty is True


def test_load_preset_clears_dirty_state():
    state = EditorState()
    state.set_binding_value("raise_right_hand", "1")

    state.load_preset("wow", "mage", "pve", {"raise_right_hand": {"input_value": "2"}})

    assert state.is_dirty is False
    assert state.current_game == "wow"


def test_discard_changes_restores_last_loaded_bindings():
    state = EditorState()
    state.load_preset("wow", "mage", "pve", {"raise_right_hand": {"input_value": "2"}})
    state.set_binding_value("raise_right_hand", "3")

    state.discard_changes()

    assert state.bindings["raise_right_hand"]["input_value"] == "2"
    assert state.is_dirty is False
