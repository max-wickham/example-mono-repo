from fastapi import Request
from fastapi.responses import JSONResponse

from libs.authentication.user_token_auth import InvalidAccessToken

from app.api.main import app

@app.exception_handler(InvalidAccessToken)
async def invalid_token_exception_handler(request: Request, exc: InvalidAccessToken):
    #TODO add logging code
    return JSONResponse(
        status_code=401,
        content={"message":"invalid access token"},
    )

class InvalidPermissionException(Exception):

    def __init__(self, token: str, data : str):
        self.tokenData = token
        self.data = data

@app.exception_handler(InvalidPermissionException)
async def invalid_permission_exception_handler(request: Request, exc: InvalidPermissionException):
    #TODO add logging code
    return JSONResponse(
        status_code=401,
        content={"message":"invalid permissions"},
    )
