'''Upload Routes'''
import io
import zipfile

from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from beanie import PydanticObjectId
from pydantic import BaseModel
from schemas.mongo_models.gesture import MongoGestureInformation

from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, s3, celery
from app.api.exceptions.not_found_exception import AccountNotFoundException
from app.api.configs import Tasks, Config
from app.api.routes.tasks import DeleteUserRestRecordingsTask, DeleteUserRecordingsTask, delete_user_recordings_task, delete_user_rest_recordings_task

GestureID = str

@app.delete('/gesuture_recordings/{gesture_id}', tags=["GestureInfo"])
async def delete_gesture_recordings(
    gesture_id: str, token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    # TODO delete gestures from S3 !!!!!
    delete_user_recordings_task.apply_async(args=[ DeleteUserRecordingsTask(
        gesture_id=gesture_id,
        account_id=str(mongo_account.id)
    ).json()], queue = Config.application_name)
    # celery.send_task(Tasks.DELETE_USER_RECORDINGS,
    # kwargs={'request' : DeleteUserRecordingsTask(
    #     account_id = str(mongo_account.id),
    #     gesture_id=gesture_id
    # ).json()})
    # if gesture_id in mongo_account.gestures:
    #     mongo_account.gestures[gesture_id].user_recordings = []
    #     mongo_account.gestures[gesture_id].processed_user_recordings = []
    #     await mongo_account.save()

@app.delete('/rest_recordings/{model_id}', tags=["GestureInfo"])
async def delete_rest_recordings(
    model_id: str, token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    delete_user_recordings_task.apply_async(args=[ DeleteUserRestRecordingsTask(
        model_id=model_id,
        account_id=str(mongo_account.id)
    ).json()], queue = Config.application_name)
    # celery.send_task(Tasks.DELETE_USER_REST_RECORDINGS,
    # kwargs={'request' : DeleteUserRestRecordingsTask(
    #     account_id = str(mongo_account.id),
    #     model_id=model_id
    # ).json()})
    # TODO delete gestures from S3 !!!!!
    # if model_id in mongo_account.models:
    #     mongo_account.models[model_id].rest_data_file_locations = []
    #     await mongo_account.save()



def download_file_from_s3(bucket, key):
    '''Download a file from s3'''
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="S3 credentials not available") from exc


@app.get('/recording_files/{gesture_id}', tags=['Gestures'])
async def get_recording_files(
    gesture_id: str, token_data: TokenData = Depends(token_authentication)):
    '''Returns back a zip file with all the recordings for the user and gesture'''
    mongo_account: MongoAccount | None = await MongoAccount.get(
        PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)

    assert gesture_id in mongo_account.gestures
    files_to_download = mongo_account.gestures[gesture_id].processed_user_recordings
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a') as zip_file:
        for file_name in files_to_download:
            file_content = download_file_from_s3('processed-recordings', file_name)
            zip_file.writestr(file_name, file_content)

    zip_buffer.seek(0)

    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment;filename=downloaded_files.zip"}
        )
