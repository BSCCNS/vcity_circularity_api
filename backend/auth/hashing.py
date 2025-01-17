#hashing.py

class Hasher():
    '''
    Wrapper for static method that hashes passwords

    '''
    @staticmethod
    def hash_passw(password: str):
        return 'fakehashed'+password
