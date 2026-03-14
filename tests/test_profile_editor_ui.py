from app.ui import SUPPORTED_ACTIONS, build_editor_rows


def test_build_editor_rows_contains_supported_actions():
    rows = build_editor_rows()

    assert "raise_right_hand" in rows
    assert set(rows) == set(SUPPORTED_ACTIONS)
