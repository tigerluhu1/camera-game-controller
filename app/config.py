from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    base_dir: Path = field(default_factory=lambda: Path.cwd())

    @property
    def profiles_dir(self) -> Path:
        return self.base_dir / "profiles"

    @property
    def settings_dir(self) -> Path:
        return self.base_dir / "settings"
