'''Task triggered when recording is uploaded'''
import time

from beanie import PydanticObjectId

from app.api.main import celery


async def process_recording_upload(
        account_id: PydanticObjectId,
        gesture_id: PydanticObjectId,
        recording_filename: str):
    '''Process the recording uploaded by a user'''
    # TODO do processing of the recording here


@celery.task(name="process_recording_upload_task")
async def process_recording_upload_task(
        account_id: PydanticObjectId,
        gesture_id: PydanticObjectId,
        recording_filename: str):
    '''Task to process the average measurements for a device'''
    await process_recording_upload(account_id, gesture_id, recording_filename)
