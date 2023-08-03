'''Upload Routes'''
import io
import uuid

from fastapi import File, UploadFile, Depends
from beanie import PydanticObjectId
from app.api.tasks.processRecordingTask import process_recording_upload_task
from schemas.mongo_models.gesture import MongoAccountGestureRecordings, MongoGestureInformation

from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, s3
from app.api.exceptions.not_found_exception import AccountNotFoundException


@app.post('/recording/{gesture_id}',tags = ["RecordingUploads"])
async def post_recording(
    gesture_id : str,
    recording: UploadFile = File(...), token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)

    gesture = await MongoGestureInformation.get(gesture_id)

    # TODO add exception if gesture not found

    filename = str(uuid.uuid4())
    contents = await recording.read()
    file_obj = io.BytesIO(contents)
    s3.upload_fileobj(file_obj, 'recordings', filename)
    if PydanticObjectId(gesture_id) not in mongo_account.gestures:
        mongo_account.gestures[PydanticObjectId(gesture_id)] = MongoAccountGestureRecordings(
            gesture_id = gesture.id,
            user_recordings = [],
        )
    mongo_account.gestures[PydanticObjectId(gesture_id)].user_recordings.append(filename)

    await process_recording_upload_task(mongo_account.id, PydanticObjectId(gesture_id), filename)
    await mongo_account.save()
