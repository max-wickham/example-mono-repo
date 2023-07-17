'''Routes for creating access tokens and validating access token'''

import time

from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import Token, TokenData, token_authentication

from app.api.authentication.authentication import authenticate_user, create_access_token
from app.api.configs.configs import environmentSettings
from app.api.main import app

@app.post('/token', response_model=Token, tags=["Token"])
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    '''Returns an auth token for an account login'''
    mongo_account = await MongoAccount.find(
        MongoAccount.email == form_data.username
    ).first_or_none()
    if mongo_account is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await mongo_account.save()
    if not authenticate_user(mongo_account, form_data.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data: TokenData = TokenData.construct()
    token_data.account_id = str(mongo_account.id)
    token_data.exp = time.time() + environmentSettings.jwt_exp
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/validate_token', tags=["Token"])
async def get_validate_token(_: TokenData = Depends(token_authentication)):
    '''Validates a token'''
    return
