from app.vision_backend import normalize_result


def test_normalize_result_handles_empty_values():
    result = normalize_result(None, None)

    assert result.landmarks == {}
    assert result.hand_states == {}


def test_normalize_result_passes_through_existing_data():
    pose = {"nose": {"x": 0.5, "y": 0.1}}
    hands = {"left": "fist"}

    result = normalize_result(pose, hands)

    assert result.landmarks == pose
    assert result.hand_states == hands
