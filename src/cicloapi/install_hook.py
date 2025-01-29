#install_hook.py


import secrets
from pathlib import Path

def generate_secret_key():
    """Generates a 32-character hexadecimal secret key."""
    return secrets.token_hex(32) 

def generate_env_variable():
    """Generates a random SECRET_KEY and saves it."""
    secret_key = generate_secret_key()

    # Save to a global .env file in the user's home directory
    env_path = Path.home() / ".venv"
    with open(env_path, "w") as f:
        f.write(f"SECRET_KEY={secret_key}\n")

    print(f"Generated SECRET_KEY and saved to {env_path}")

# Run this function when the script is executed
if __name__ == "__main__":
    generate_env_variable()