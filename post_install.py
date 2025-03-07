import os

if __name__ == "__main__":

    secret_key = os.urandom(32).hex()
    os.environ["SECRET_KEY"] = secret_key
    with open(".env", "a") as env_file:
        env_file.write(f"SECRET_KEY={secret_key}\n")

print('Environment file with secret key for hashing created/updated.')