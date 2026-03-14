from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

from app.detection import LandmarkPoint


@dataclass(slots=True)
class VisionResult:
    landmarks: dict
    hand_states: dict


def normalize_result(pose_landmarks, hand_states) -> VisionResult:
    if isinstance(pose_landmarks, dict) and isinstance(hand_states, dict):
        return VisionResult(
            landmarks=pose_landmarks or {},
            hand_states=hand_states or {},
        )

    landmarks = _normalize_pose_landmarks(pose_landmarks)
    states = _normalize_hand_states(hand_states)
    return VisionResult(
        landmarks=landmarks,
        hand_states=states,
    )


def _normalize_pose_landmarks(pose_result) -> dict[str, LandmarkPoint]:
    if pose_result is None:
        return {}
    raw_landmarks = []
    if hasattr(pose_result, "pose_landmarks"):
        pose_landmarks = pose_result.pose_landmarks
        if isinstance(pose_landmarks, list):
            raw_landmarks = pose_landmarks[0] if pose_landmarks else []
        else:
            raw_landmarks = getattr(pose_landmarks, "landmark", [])
    if not raw_landmarks:
        return {}

    landmarks: dict[str, LandmarkPoint] = {}
    if len(raw_landmarks) > 24:
        index_map = {
            "nose": 0,
            "left_shoulder": 11,
            "right_shoulder": 12,
            "left_wrist": 15,
            "right_wrist": 16,
        }
        for name, index in index_map.items():
            point = raw_landmarks[index]
            landmarks[name] = LandmarkPoint(x=point.x, y=point.y)
        left_hip = raw_landmarks[23]
        right_hip = raw_landmarks[24]
        landmarks["hip_center"] = LandmarkPoint(
            x=(left_hip.x + right_hip.x) / 2,
            y=(left_hip.y + right_hip.y) / 2,
        )
        return landmarks

    fallback_names = ["nose", "hip_center", "right_wrist", "right_shoulder"]
    for name, point in zip(fallback_names, raw_landmarks):
        landmarks[name] = LandmarkPoint(x=point.x, y=point.y)
    return landmarks


def _normalize_hand_states(hands_result) -> dict[str, str]:
    if hands_result is None:
        return {}
    landmarks_list = (
        getattr(hands_result, "multi_hand_landmarks", None)
        or getattr(hands_result, "hand_landmarks", None)
        or []
    )
    handedness_list = (
        getattr(hands_result, "multi_handedness", None)
        or getattr(hands_result, "handedness", None)
        or []
    )
    states: dict[str, str] = {}
    for hand_landmarks, handedness in zip(landmarks_list, handedness_list):
        if isinstance(handedness, list):
            handedness = handedness[0] if handedness else None
        if handedness is None:
            label = "right"
        else:
            label = getattr(handedness.classification[0], "label", None)
            if label is None:
                label = getattr(handedness, "category_name", "Right")
            label = str(label).lower()
        hand_points = getattr(hand_landmarks, "landmark", hand_landmarks)
        states[label] = _infer_hand_state(hand_points)
    return states


def _infer_hand_state(landmarks) -> str:
    if len(landmarks) < 21:
        return "open_palm"
    tip_indices = [8, 12, 16, 20]
    pip_indices = [6, 10, 14, 18]
    extended = sum(
        1
        for tip_index, pip_index in zip(tip_indices, pip_indices)
        if landmarks[tip_index].y < landmarks[pip_index].y
    )
    return "open_palm" if extended >= 2 else "fist"


class MediaPipeVisionBackend:
    _DEFAULT = object()

    def __init__(self, pose_backend=None, hands_backend=None, cv2_module=_DEFAULT, models_dir: Path | None = None):
        self.cv2_module = self._load_cv2() if cv2_module is self._DEFAULT else cv2_module
        self.models_dir = models_dir or Path.cwd() / "models"
        self.pose_backend = pose_backend
        self.hands_backend = hands_backend

    @staticmethod
    def _load_cv2():
        try:
            import cv2
        except ImportError:
            return None
        return cv2

    @staticmethod
    def _load_mediapipe():
        try:
            import mediapipe as mp
        except ImportError:
            return None
        return mp

    def _create_pose_backend(self):
        mp = self._load_mediapipe()
        if mp is None:
            return None
        if hasattr(mp, "solutions"):
            return mp.solutions.pose.Pose()
        try:
            base_options = mp.tasks.BaseOptions(
                model_asset_path=str(self._ensure_model("pose_landmarker_lite.task", self._pose_model_url()))
            )
            options = mp.tasks.vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
            )
            return mp.tasks.vision.PoseLandmarker.create_from_options(options)
        except Exception:
            return None

    def _create_hands_backend(self):
        mp = self._load_mediapipe()
        if mp is None:
            return None
        if hasattr(mp, "solutions"):
            return mp.solutions.hands.Hands(max_num_hands=2)
        try:
            base_options = mp.tasks.BaseOptions(
                model_asset_path=str(self._ensure_model("hand_landmarker.task", self._hand_model_url()))
            )
            options = mp.tasks.vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_hands=2,
            )
            return mp.tasks.vision.HandLandmarker.create_from_options(options)
        except Exception:
            return None

    def process_frame(self, frame) -> VisionResult:
        if self.pose_backend is None:
            self.pose_backend = self._create_pose_backend()
        if self.hands_backend is None:
            self.hands_backend = self._create_hands_backend()
        if frame is None or self.pose_backend is None or self.hands_backend is None:
            return VisionResult({}, {})
        rgb_frame = frame
        if self.cv2_module is not None:
            rgb_frame = self.cv2_module.cvtColor(frame, self.cv2_module.COLOR_BGR2RGB)
        pose_result = self._process_pose(rgb_frame)
        hands_result = self._process_hands(rgb_frame)
        return normalize_result(pose_result, hands_result)

    def _process_pose(self, frame):
        if hasattr(self.pose_backend, "detect"):
            mp = self._load_mediapipe()
            if mp is None:
                return None
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            return self.pose_backend.detect(image)
        return self.pose_backend.process(frame)

    def _process_hands(self, frame):
        if hasattr(self.hands_backend, "detect"):
            mp = self._load_mediapipe()
            if mp is None:
                return None
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            return self.hands_backend.detect(image)
        return self.hands_backend.process(frame)

    def _ensure_model(self, filename: str, url: str) -> Path:
        self.models_dir.mkdir(parents=True, exist_ok=True)
        target = self.models_dir / filename
        if not target.exists():
            urlretrieve(url, target)
        return target

    @staticmethod
    def _pose_model_url() -> str:
        return "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"

    @staticmethod
    def _hand_model_url() -> str:
        return "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
