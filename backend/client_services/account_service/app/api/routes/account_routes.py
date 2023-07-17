'''Account Routes'''
import time

from fastapi.params import Depends
from fastapi import Body
from pydantic import BaseModel
from pydantic.fields import Field
import jwt
from beanie import PydanticObjectId

from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app
from app.api.exceptions.not_found_exception import AccountNotFoundException


class AccountInfo(BaseModel):
    '''Basic Account Info'''
    name: str
    email: str

@app.get('/account', response_model=AccountInfo)
async def get_accounts(token_data: TokenData = Depends(token_authentication)) -> AccountInfo:
    '''Return the information regarding the current users account'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    return AccountInfo(
        name = mongo_account.name,
        email = mongo_account.email
    )
