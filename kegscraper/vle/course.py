from __future__ import annotations

from dataclasses import dataclass

from . import session

@dataclass
class Course:
    id: int = None
    _sess: session.Session = None
