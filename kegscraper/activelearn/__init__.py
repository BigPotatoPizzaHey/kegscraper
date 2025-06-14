from __future__ import annotations

import os
import sys

from .session import Session, login

_result = os.system(f"\"{sys.executable}\" -m playwright install")
