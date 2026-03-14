from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


Detector = Callable[[Any], dict]
Mapper = Callable[[set[str], Any], None]


@dataclass(slots=True)
class ControllerStatus:
    running: bool = False
    actions: set[str] = field(default_factory=set)


class Controller:
    def __init__(self, detector: Detector, mapper: Mapper):
        self.detector = detector
        self.mapper = mapper
        self.status = ControllerStatus()

    def start(self) -> None:
        self.status.running = True

    def stop(self) -> None:
        self.status.running = False
        self.status.actions = set()

    def process_frame(self, frame: Any, preset: Any) -> dict:
        result = self.detector(frame)
        actions = set(result.get("actions", set()))
        self.status.actions = actions
        if self.status.running:
            self.mapper(actions, preset)
        return {"actions": actions, "running": self.status.running}
