from app.vision_backend import MediaPipeVisionBackend, normalize_result


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


def test_normalize_result_extracts_pose_and_hand_state_from_backend_objects():
    class FakeLandmark:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class FakePose:
        pose_landmarks = type(
            "PoseLandmarks",
            (),
            {"landmark": [FakeLandmark(0.5, 0.2), FakeLandmark(0.52, 0.65), FakeLandmark(0.7, 0.1), FakeLandmark(0.7, 0.45)]},
        )()

    class FakeHandedness:
        classification = [type("Cls", (), {"label": "Right"})()]

    class FakeHandLandmarks:
        landmark = [FakeLandmark(0.7, 0.1)] * 21

    result = normalize_result(
        FakePose(),
        type(
            "HandsResult",
            (),
            {
                "multi_hand_landmarks": [FakeHandLandmarks()],
                "multi_handedness": [FakeHandedness()],
            },
        )(),
    )

    assert "nose" in result.landmarks
    assert "hip_center" in result.landmarks
    assert result.hand_states["right"] in {"fist", "open_palm"}


def test_mediapipe_backend_process_frame_uses_injected_backends():
    class FakePoseBackend:
        def process(self, _frame):
            return type(
                "PoseResult",
                (),
                {
                    "pose_landmarks": type(
                        "PoseLandmarks",
                        (),
                        {"landmark": [type("Point", (), {"x": 0.5, "y": 0.2})(), type("Point", (), {"x": 0.52, "y": 0.65})()]},
                    )()
                },
            )()

    class FakeHandsBackend:
        def process(self, _frame):
            return None

    backend = MediaPipeVisionBackend(
        pose_backend=FakePoseBackend(),
        hands_backend=FakeHandsBackend(),
        cv2_module=None,
    )

    result = backend.process_frame("frame")

    assert "nose" in result.landmarks
