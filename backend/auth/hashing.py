#hashing.py

class Hasher():
    @staticmethod
    def hash_passw(password: str):
        return 'fakehashed'+password

    @staticmethod
    def check_passw(stored_password: str, hashed_password: str):
        return stored_password == hashed_password