'''Task to complete a request to fine train a model'''
import sys
sys.path.insert(0,'/')

import asyncio
import io
import json

import keras
import boto3
from celery import Celery, shared_task
from beanie import init_beanie
from beanie.odm.fields import PydanticObjectId
import motor
from asgiref.sync import async_to_sync

from schemas.task_messages.model_training_task import TrainModelRequest
from schemas.mongo_models.training_models import MongoTrainingModel, TrainingState
from schemas.mongo_models.account_models import MongoAccount
from configs.commons import Tasks

from src.configs.configs import environmentSettings

#############  Configure S3

if environmentSettings.ENV == 'DEV':
    import os
    os.environ['S3_USE_SIGV4'] = 'True'
    s3 = boto3.client('s3',
                      endpoint_url=environmentSettings.S3_URL,
                      aws_access_key_id=environmentSettings.S3_ID,
                      aws_secret_access_key=environmentSettings.S3_KEY
                      )
else:
    s3 = boto3.client('s3',
                      region_name=environmentSettings.S3_REGION,
                      endpoint_url=environmentSettings.S3_URL,
                      aws_access_key_id=environmentSettings.S3_ID,
                      aws_secret_access_key=environmentSettings.S3_KEY)

try:
    s3.create_bucket(Bucket='models')
except Exception:
    print('unable to create bucket')
############# Configure Celery

global_celery = Celery(Tasks.GLOBAL_CELERY_SERVICE)
global_celery.conf.broker_url = environmentSettings.CELERY_BROKER_URL
global_celery.conf.result_backend = environmentSettings.CELERY_RESULT_BACKEND

############# Configure Beanie



async def configure_beanie():
    '''Setup the database connection'''
    client = motor.motor_asyncio.AsyncIOMotorClient(environmentSettings.mongo_database_url)
    await init_beanie(
        database=client['test']
        if environmentSettings.ENV == 'DEV'
        else client['main'],
        document_models=[MongoTrainingModel, MongoAccount])

# asyncio.run(asyncio.new_event_loop())


############# Define the Celery task

async def model_training(request: TrainModelRequest):
    '''Async Task'''
    await configure_beanie()
    print(request)
    print(asyncio.get_event_loop())
    training_model = await MongoTrainingModel.get(PydanticObjectId(request.training_model_id))
    # set status to in progress
    training_model.training_state = TrainingState.IN_PROGRESS
    await training_model.save()
    # load the training data
    training_data = await load_data(training_model)
    # create and train the model
    model = await train_model(training_data, training_model)
    # upload the model to the database
    await upload_model_to_database(model, training_model)
    # set the status to complete
    training_model.training_state = TrainingState.COMPLETE
    await training_model.save()


@global_celery.task(name=Tasks.MODEL_TRAINING_TASK)
def model_training_task(request: str):
    '''Train a new model'''
    print(request)
    asyncio.set_event_loop(asyncio.new_event_loop())
    request = TrainModelRequest(**json.loads(request))
    asyncio.run(model_training(request))

############# Processing Functions

async def load_data(training_model: MongoTrainingModel):
    '''
    Load the training data from S3 storage and construct a numpy array using it
    The data needs to be converted from binary form to the correct format
    '''
    data : dict[PydanticObjectId,bytes] = {}

    mongo_account = await MongoAccount.get(training_model.account_id)

    gestures = training_model.gestures
    print(mongo_account.gestures)
    print(training_model)
    for gesture in gestures:
        recordings = mongo_account.gestures[gesture.gesture_id]
        data[gesture.gesture_id] = []
        for recording_filename in recordings.processed_user_recordings:
            s3_object = s3.get_object(Bucket='processed-recordings', Key=recording_filename)
            body = s3_object['Body']
            data[gesture.gesture_id].append(body.read())
    print(data)
    # TODO process the binary data, turn into a numpy array or something


async def train_model(training_data, mongo_training_model: MongoTrainingModel) -> keras.Model:
    '''
    Train the model using the training data
    The model output dimensions need to be dictated by the number of gestures
    '''
    # TODO create and train the model



async def upload_model_to_database(model: keras.Model, mongo_training_model: MongoTrainingModel):
    '''Upload the trained model file to the database'''
    model.save('/src/models/model')
    with open('/src/models/model', 'wb') as model_file:
        model_bytes = model_file.read()
        filename = mongo_training_model.model_file_name
        file_obj = io.BytesIO(model_bytes)
        s3.upload_fileobj(file_obj, 'models', filename)
