SUPPORTED_ACTIONS = [
    "lean_left",
    "lean_right",
    "raise_left_hand",
    "raise_right_hand",
    "both_hands_up",
    "crouch",
    "left_fist",
    "right_fist",
    "left_open_palm",
    "right_open_palm",
    "mouse_move",
]


def build_editor_rows() -> list[str]:
    return list(SUPPORTED_ACTIONS)
