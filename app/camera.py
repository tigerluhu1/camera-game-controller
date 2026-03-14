from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(slots=True)
class CameraStatus:
    running: bool = False
    frame_size: tuple[int, int] = (0, 0)
    last_error: str = ""


class Camera:
    def __init__(self, backend_factory: Callable[[int], Any] | None = None, device_index: int = 0):
        self.status = CameraStatus()
        self.backend_factory = backend_factory or self._default_backend_factory
        self.device_index = device_index
        self._capture: Any = None

    def open(self) -> CameraStatus:
        self._capture = self.backend_factory(self.device_index)
        if self._capture is None:
            self.status = CameraStatus(running=False, last_error="Camera backend unavailable")
            return self.status
        if hasattr(self._capture, "isOpened") and not self._capture.isOpened():
            self.status = CameraStatus(running=False, last_error="Unable to open camera")
            return self.status
        self.status = CameraStatus(running=True)
        return self.status

    def read(self) -> Any:
        if self._capture is None:
            return None
        if hasattr(self._capture, "read"):
            ok, frame = self._capture.read()
            if not ok:
                return None
            if hasattr(frame, "shape") and len(frame.shape) >= 2:
                self.status.frame_size = (int(frame.shape[1]), int(frame.shape[0]))
            return frame
        return None

    def close(self) -> None:
        if self._capture is not None and hasattr(self._capture, "release"):
            self._capture.release()
        self._capture = None
        self.status = CameraStatus(running=False)

    @staticmethod
    def _default_backend_factory(device_index: int):
        try:
            import cv2
        except ImportError:
            return None
        return cv2.VideoCapture(device_index)
