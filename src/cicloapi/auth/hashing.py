# hashing.py

import bcrypt

# Class containing methods to hash passwords


class Hasher:
    """
    Wrapper class for static method that hashes passwords

    """

    @staticmethod
    def hash_passw(password):
        """
        Hashes the password using the Bcrypt algorithm

        Parameters:
            password (str): Plain password in string format

        Returns:
            str: Password hashed
        """
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return hashed_password

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verifies the validity of a given password against a hashed one.

        Parameters:
            plain_password (str): Plain password in string format
            hashed_password (bytes): Hashed password in bytes format

        Returns:
            boolean: True if hashed(plain_password) = = hashed_password. False otherwise.



        """
        password_byte_enc = plain_password.encode("utf-8")
        return bcrypt.checkpw(
            password=password_byte_enc, hashed_password=hashed_password
        )
