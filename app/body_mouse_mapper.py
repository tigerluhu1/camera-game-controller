from __future__ import annotations


class BodyMouseMapper:
    """Compute mouse deltas by tracking a selected body anchor."""

    SHOULDERS = "shoulders"
    HEAD = "head"
    VALID_ANCHORS = {SHOULDERS, HEAD}

    def __init__(self, anchor: str = SHOULDERS):
        self.anchor = anchor if anchor in self.VALID_ANCHORS else self.SHOULDERS

    def compute_mouse_delta(self, landmarks: dict, frame_size: tuple[int, int]) -> tuple[int, int]:
        anchor_point = self._anchor_point(landmarks)
        if anchor_point is None:
            return (0, 0)

        width, height = frame_size
        center_x = width / 2
        center_y = height / 2
        anchor_x = anchor_point[0] * width
        anchor_y = anchor_point[1] * height
        delta_x = anchor_x - center_x
        delta_y = anchor_y - center_y

        return (int(round(delta_x)), int(round(delta_y)))

    def _anchor_point(self, landmarks: dict) -> tuple[float, float] | None:
        if self.anchor == self.HEAD:
            return self._as_point(landmarks.get("nose"))

        left = landmarks.get("left_shoulder")
        right = landmarks.get("right_shoulder")
        left_point = self._as_point(left)
        right_point = self._as_point(right)
        if left_point and right_point:
            return ((left_point[0] + right_point[0]) / 2, (left_point[1] + right_point[1]) / 2)

        return self._as_point(landmarks.get("nose"))

    @staticmethod
    def _as_point(value) -> tuple[float, float] | None:
        if value is None:
            return None
        if hasattr(value, "x") and hasattr(value, "y"):
            return (float(value.x), float(value.y))
        if isinstance(value, tuple) or isinstance(value, list):
            if len(value) >= 2:
                return (float(value[0]), float(value[1]))
        return None
