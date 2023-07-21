'''Upload Routes'''
import io
import uuid

from fastapi import File, UploadFile, Depends
from beanie import PydanticObjectId

from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, s3
from app.api.exceptions.not_found_exception import AccountNotFoundException




def process_data(data):
    ...





@app.post('/recording')
async def post_recording(
    recording: UploadFile = File(...), token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)

    filename = str(uuid.uuid4())
    contents = await recording.read()
    file_obj = io.BytesIO(contents)
    s3.upload_fileobj(file_obj, 'recordings', filename)
    mongo_account.recording_files.append(filename)
