from typing import Generator


class VectorDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = {}
        return cls._instance


def get_db() -> Generator:
    try:
        db = VectorDB()
        print("Opening db connection " + str(id(db)))
        yield db
    finally:
        print("Closing db connection " + str(id(db)))