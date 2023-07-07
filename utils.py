import requests
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
EMAILHUNTER_API_KEY = settings.EMAILHUNTER_API_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Veryfying password with hashed password from db
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """
    Returns encoded jwt token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_email(email: str) -> bool:
    """
    Checks if email is valid.
    """
    try:
        res = requests.get((
            'https://api.hunter.io/v2/email-verifier?'
            f'email={email}&api_key={EMAILHUNTER_API_KEY}'
        )).json()
        return res["data"]["status"] == "valid"
    except requests.exceptions.ConnectTimeout:
        raise requests.exceptions.ConnectTimeout(
            "Connection to hunter.io timed out. Please try later")
