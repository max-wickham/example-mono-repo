from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.main import app


class AccountNotFoundException(Exception):
    def __init__(self, account_id: str):
        self.account_id = account_id

@app.exception_handler(AccountNotFoundException)
async def account_not_found_exception_handler(request: Request, exc: AccountNotFoundException):
    #TODO add logging code
    return JSONResponse(
        status_code=404,
        content={"account_id": exc.account_id},
    )
