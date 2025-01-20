#user_methods.py

def get_current_user(token: str) -> str:

    try:
        decoded_token =  jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    return decoded_token['user']



