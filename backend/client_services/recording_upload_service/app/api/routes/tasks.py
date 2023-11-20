'''Background Tasks'''

import asyncio
import json

from beanie import PydanticObjectId, init_beanie
from pydantic import BaseModel
import motor

from schemas.mongo_models.account_models import MongoAccount
from schemas.mongo_models.pre_made_models import MongoPreMadeModel
from schemas.mongo_models.gesture import MongoGestureInformation

from app.api.configs import Tasks, environmentSettings
from app.api.main import celery, s3


beanie_setup = False
async def setup_beanie():
    global beanie_setup
    if not beanie_setup:
        client = motor.motor_asyncio.AsyncIOMotorClient(environmentSettings.MONGO_DATABASE_URL)  # type: ignore
        await init_beanie(
            database=client['test']
            if environmentSettings.ENV == 'DEV'
            else client['main'],
            document_models=[MongoGestureInformation, MongoAccount,MongoPreMadeModel])  # type: ignore
        beanie_setup = True



class DeleteUserRecordingsTask(BaseModel):
    '''Request to delete recordings'''
    gesture_id: str
    account_id: str

class DeleteUserRestRecordingsTask(BaseModel):
    '''Request to delete recordings'''
    model_id: str
    account_id: str

async def delete_user_recordings(task: DeleteUserRecordingsTask):
    await setup_beanie()
    mongo_account = await MongoAccount.get(PydanticObjectId(task.account_id))
    if mongo_account is None:
        return
    if task.gesture_id in mongo_account.gestures:
        for recording in mongo_account.gestures[task.gesture_id].user_recordings:
            try:
                s3.delete_object(Bucket='recordings', Key=recording)
            except:
                pass
        for recording in mongo_account.gestures[task.gesture_id].processed_user_recordings:
            try:
                s3.delete_object(Bucket='processed-recordings', Key=recording)
            except:
                pass
    # mongo_account.gestures.pop(task.gesture_id)
    mongo_account.gestures[task.gesture_id].user_recordings = []
    mongo_account.gestures[task.gesture_id].processed_user_recordings = []
    await mongo_account.save()

@celery.task(name=Tasks.DELETE_USER_RECORDINGS)
def delete_user_recordings_task(request: str):
    '''Train a new model'''
    try:
        asyncio.get_event_loop().close()
        asyncio.set_event_loop(asyncio.new_event_loop())
    except:
        ...
    task = DeleteUserRecordingsTask(**json.loads(request))
    asyncio.run(delete_user_recordings(task))


async def delete_user_rest_recordings(task: DeleteUserRestRecordingsTask):
    await setup_beanie()
    mongo_account = await MongoAccount.get(PydanticObjectId(task.account_id))
    if mongo_account is None:
        return
    if task.model_id in mongo_account.models:
        for recording in mongo_account.models[task.model_id].rest_data_file_locations:
            try:
                s3.delete_object(Bucket='recordings', Key=recording)
            except:
                pass
    # mongo_account.gestures.pop(task.gesture_id)
    mongo_account.models[task.model_id].rest_data_file_locations = []
    await mongo_account.save()

@celery.task(name=Tasks.DELETE_USER_REST_RECORDINGS)
def delete_user_rest_recordings_task(request: str):
    '''Train a new model'''
    try:
        asyncio.get_event_loop().close()
        asyncio.set_event_loop(asyncio.new_event_loop())
    except:
        ...
    task = DeleteUserRestRecordingsTask(**json.loads(request))
    asyncio.run(delete_user_rest_recordings(task))
