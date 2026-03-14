from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class VisionResult:
    landmarks: dict
    hand_states: dict


def normalize_result(pose_landmarks, hand_states) -> VisionResult:
    return VisionResult(
        landmarks=pose_landmarks or {},
        hand_states=hand_states or {},
    )
