from .session import Session, login


import os
import sys

_result = os.system(f"\"{sys.executable}\" -m playwright install")
