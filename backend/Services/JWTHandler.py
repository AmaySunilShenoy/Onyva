# JWT 
from datetime import timezone, timedelta, datetime
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

class JWT:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
    ALGORITHM = os.getenv("ALGORITHM")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.JWT_SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt
    
    @classmethod
    def create_refresh_token(cls, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=cls.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.JWT_REFRESH_SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt
    
    @classmethod
    def decode_token(cls, token: str) -> Any:
        try:
            print('next here')
            print(token)
            payload = jwt.decode(token, cls.JWT_SECRET_KEY, algorithms=[cls.ALGORITHM])
            print(payload)
            return payload
        except jwt.JWTError as e:
            print(f"Error decoding JWT token: {e}")
            return None

            
    @classmethod
    def get_user_id(cls, token: str) -> str:
        try:
            payload = cls.decode_token(token)
            print(payload)
            if payload and "sub" in payload:
                return payload["sub"]
            return None
        except Exception as e:
            print(f"Error getting user ID from token: {e}")
            return None
        
    

