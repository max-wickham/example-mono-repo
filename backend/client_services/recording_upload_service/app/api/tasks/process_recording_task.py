'''Task triggered when recording is uploaded'''

import uuid
import io

from beanie import PydanticObjectId

from schemas.mongo_models.account_models import MongoAccount

from app.api.main import celery, s3


async def process_recording_upload(
        account_id: PydanticObjectId,
        gesture_id: str,
        recording_filename: str):
    '''Process the recording uploaded by a user'''
    print('Running Process Recordings Task')
    # TODO do processing of the recording here
    # TODO load the recording
    # store the processed recording filename in processed_recordings
    recording = s3.get_object(Bucket='recordings', Key=recording_filename)['Body'].read()
    # TODO can be whatever format and then converted to bytes
    # (i.e. pickle a python object then read the bytes for instance)

    # Save the processed recording and then store the filename in the user gesture model
    processed_recording = recording
    filename = str(uuid.uuid4())
    file_obj = io.BytesIO(processed_recording)
    s3.upload_fileobj(file_obj, 'processed-recordings', filename)
    mongo_account = await MongoAccount.get(account_id)
    mongo_account.gestures[str(gesture_id)].processed_user_recordings.append(filename)
    await mongo_account.save()

@celery.task(name="process_recording_upload_task")
async def process_recording_upload_task(
        account_id: PydanticObjectId,
        gesture_id: str,
        recording_filename: str):
    '''Task to process the average measurements for a device'''
    await process_recording_upload(account_id, gesture_id, recording_filename)
