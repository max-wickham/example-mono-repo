'''Background Tasks'''

import asyncio
import json

from pydantic import BaseModel
import motor
from beanie import init_beanie

from schemas.mongo_models.account_models import MongoAccount
from schemas.mongo_models.pre_made_models import MongoPreMadeModel
from schemas.mongo_models.gesture import MongoGestureInformation

from app.api.configs import environmentSettings
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


class DeleteRecordingsTask(BaseModel):
    '''Request to delete recordings'''
    gesture_id: str

async def delete_recordings(task: DeleteRecordingsTask):
    await setup_beanie()
    async for mongo_account in MongoAccount.find_all():
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
        mongo_account.gestures.pop(task.gesture_id)
        await mongo_account.save()

@celery.task()
def delete_recordings_task(request: str):
    '''Train a new model'''
    try:
        try:
            asyncio.get_event_loop().close()
            asyncio.set_event_loop(asyncio.new_event_loop())
        except:
            ...
        delete_recordings_task = DeleteRecordingsTask(**json.loads(request))
        asyncio.run(delete_recordings(delete_recordings_task))
    except:
        ...
