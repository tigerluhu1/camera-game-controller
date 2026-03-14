from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CameraStatus:
    running: bool = False
    frame_size: tuple[int, int] = (0, 0)
    last_error: str = ""


class Camera:
    def __init__(self):
        self.status = CameraStatus()
        self._capture: Any = None

    def open(self) -> CameraStatus:
        self.status = CameraStatus(running=True)
        return self.status

    def read(self) -> Any:
        return None

    def close(self) -> None:
        self.status = CameraStatus(running=False)
