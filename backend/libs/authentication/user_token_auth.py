import time
from typing import Optional

from fastapi.params import Depends
from app.api.configs.configs import environmentSettings
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel

class InvalidAccessToken(Exception):
    def __init__(self, token: str, data : str):
        self.tokenData = token
        self.data = data

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    token_type : str = 'user'
    account_id: str
    exp : int

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=environmentSettings.token_url)

async def token_authentication(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload = jwt.decode(token, environmentSettings.jwt_secret, algorithms=[environmentSettings.jwt_algorithm])
        tokenData = TokenData(**payload)

        if tokenData.exp < int(time.time()): raise InvalidAccessToken(token, "expired")
        return tokenData
    except:
        pass
    raise InvalidAccessToken(token, "find token")
