import numpy as np

from app.detection import LandmarkPoint
from app.preview import render_preview_frame


def test_render_preview_frame_returns_pil_image():
    frame = np.zeros((40, 60, 3), dtype="uint8")

    image = render_preview_frame(frame, {}, set())

    assert image.size == (60, 40)


def test_render_preview_frame_draws_with_landmarks_and_actions():
    frame = np.zeros((40, 60, 3), dtype="uint8")
    landmarks = {
        "nose": LandmarkPoint(x=0.5, y=0.1),
        "hip_center": LandmarkPoint(x=0.5, y=0.8),
        "right_shoulder": LandmarkPoint(x=0.7, y=0.4),
        "right_wrist": LandmarkPoint(x=0.8, y=0.2),
    }

    image = render_preview_frame(frame, landmarks, {"raise_right_hand"})

    assert image.size == (60, 40)
