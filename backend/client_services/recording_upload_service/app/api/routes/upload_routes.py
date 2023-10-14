'''Upload Routes'''
import io
import uuid

from fastapi import File, UploadFile, Depends
from beanie import PydanticObjectId
from app.api.tasks.process_recording_task import process_recording_upload_task
from schemas.mongo_models.pre_made_models import MongoPreMadeModel
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.account_models import MongoAccountGestureRecordings

from schemas.mongo_models.account_models import MongoAccount, UserFineTunedModel
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, s3
from app.api.exceptions.not_found_exception import AccountNotFoundException


@app.post('/recording/{gesture_id}',tags = ["RecordingUploads"])
async def post_recording(
    gesture_id : str,
    recording: UploadFile = File(...), token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data'''

    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None or mongo_account.id is None:
        raise AccountNotFoundException(token_data.account_id)

    gesture : MongoGestureInformation | None = await MongoGestureInformation.get(PydanticObjectId(gesture_id))
    if gesture is None or gesture.id is None:
        raise Exception

    filename = str(uuid.uuid4())
    contents = await recording.read()
    file_obj = io.BytesIO(contents)
    s3.upload_fileobj(file_obj, 'recordings', filename)
    if gesture_id not in mongo_account.gestures:
        mongo_account.gestures[gesture_id] = MongoAccountGestureRecordings(
            gesture_id = gesture.id,
            user_recordings = [],
        )
    mongo_account.gestures[gesture_id].user_recordings.append(filename)

    await mongo_account.save()
    await process_recording_upload_task(mongo_account.id, gesture_id, filename)


@app.post('/rest_recording/{model_id}',tags = ["RecordingUploads"])
async def post_rest_recording(
    model_id : str,
    recording: UploadFile = File(...), token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data as rest data for a model'''

    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None or mongo_account.id is None:
        raise AccountNotFoundException(token_data.account_id)

    pre_made_model : MongoPreMadeModel | None = await MongoPreMadeModel.get(PydanticObjectId(model_id))
    if pre_made_model is None or pre_made_model.id is None:
        raise Exception

    filename = str(uuid.uuid4())
    contents = await recording.read()
    file_obj = io.BytesIO(contents)
    s3.upload_fileobj(file_obj, 'recordings', filename)

    if model_id not in mongo_account.models:
        # TODO do this as a method in the user class !!!!!!!!
        mongo_account.models[model_id] = UserFineTunedModel(
            name = 'na',
            pre_made_model_id=PydanticObjectId(model_id),
            model_location=str(uuid.uuid4())
        )
    mongo_account.models[model_id].rest_data_file_locations.append(filename)

    await mongo_account.save()
