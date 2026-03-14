from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LandmarkPoint:
    x: float
    y: float


def _is_hand_raised(landmarks: dict[str, LandmarkPoint], side: str) -> bool:
    wrist = landmarks.get(f"{side}_wrist")
    shoulder = landmarks.get(f"{side}_shoulder")
    if wrist is None or shoulder is None:
        return False
    return wrist.y < shoulder.y - 0.1


def detect_actions(
    landmarks: dict[str, LandmarkPoint],
    hand_states: dict[str, str],
) -> set[str]:
    actions: set[str] = set()

    if _is_hand_raised(landmarks, "left"):
        actions.add("raise_left_hand")
    if _is_hand_raised(landmarks, "right"):
        actions.add("raise_right_hand")
    if {"raise_left_hand", "raise_right_hand"}.issubset(actions):
        actions.add("both_hands_up")

    nose = landmarks.get("nose")
    hip_center = landmarks.get("hip_center")
    if nose is not None and hip_center is not None:
        if nose.x < hip_center.x - 0.1:
            actions.add("lean_left")
        elif nose.x > hip_center.x + 0.1:
            actions.add("lean_right")
        if nose.y > hip_center.y - 0.25:
            actions.add("crouch")

    for side, state in hand_states.items():
        if state == "fist":
            actions.add(f"{side}_fist")
        if state == "open_palm":
            actions.add(f"{side}_open_palm")

    return actions
