import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.db import engine

try:
    with engine.connect() as conn:
        print("Connected!")
except Exception as e:
    print("Connection failed:")
    print(e)