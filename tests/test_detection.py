from app.detection import LandmarkPoint, detect_actions


def test_detect_actions_detects_raise_right_hand():
    landmarks = {
        "right_wrist": LandmarkPoint(x=0.7, y=0.2),
        "right_shoulder": LandmarkPoint(x=0.7, y=0.45),
    }

    actions = detect_actions(landmarks, hand_states={})

    assert "raise_right_hand" in actions


def test_detect_actions_detects_lean_left_and_left_fist():
    landmarks = {
        "nose": LandmarkPoint(x=0.35, y=0.2),
        "hip_center": LandmarkPoint(x=0.55, y=0.65),
    }

    actions = detect_actions(landmarks, hand_states={"left": "fist"})

    assert "lean_left" in actions
    assert "left_fist" in actions


def test_detect_actions_detects_both_hands_up():
    landmarks = {
        "left_wrist": LandmarkPoint(x=0.3, y=0.1),
        "left_shoulder": LandmarkPoint(x=0.3, y=0.45),
        "right_wrist": LandmarkPoint(x=0.7, y=0.1),
        "right_shoulder": LandmarkPoint(x=0.7, y=0.45),
    }

    actions = detect_actions(landmarks, hand_states={})

    assert "both_hands_up" in actions
