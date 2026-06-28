from db import engine

try:
    with engine.connect() as conn:
        print("Connected!")
except Exception as e:
    print("Connection failed:")
    print(e)