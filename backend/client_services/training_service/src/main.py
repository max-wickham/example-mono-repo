'''Task to complete a request to fine train a model'''
import pickle
import sys; sys.path.insert(0,'/')
import uuid
import asyncio
import json

import boto3
from celery import Celery
from beanie import init_beanie
from beanie.odm.fields import PydanticObjectId
import motor
import numpy as np
import tensorflow as tf


from schemas.task_messages.model_training_task import TrainModelRequest
from schemas.mongo_models.pre_made_models import MongoPreMadeModel
from schemas.mongo_models.account_models import MongoAccount, TrainingState, UserFineTunedModel
from configs.commons import Tasks

from src.configs import environmentSettings

EPOCH_NUMS = 200


#############  Configure S3

if environmentSettings.ENV == 'DEV':
    import os
    os.environ['S3_USE_SIGV4'] = 'True'
    s3 = boto3.client('s3',
                      endpoint_url=environmentSettings.S3_URL,
                      aws_access_key_id=environmentSettings.S3_ID,
                      aws_secret_access_key=environmentSettings.S3_KEY
                      )
    s3_resource = boto3.resource('s3',
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
        document_models=[MongoPreMadeModel, MongoAccount])

# asyncio.run(asyncio.new_event_loop())


############# Define the Celery task

async def model_training(request: TrainModelRequest):
    '''Async Task'''
    await configure_beanie()
    account = await MongoAccount.get(PydanticObjectId(request.account_id))
    if account is None:
        raise Exception
    if request.training_model_id not in account.models:
        account.models[request.training_model_id] = UserFineTunedModel(
            name = 'na',
            pre_made_model_id=PydanticObjectId(request.training_model_id),
        )

    account.models[request.training_model_id].training_state = TrainingState.IN_PROGRESS
    account.models[request.training_model_id].model_location=str(uuid.uuid4())
    await account.save()
    account = await MongoAccount.get(PydanticObjectId(request.account_id))
    if account is None:
        raise Exception

    pre_trainined_model = await MongoPreMadeModel.get(PydanticObjectId(request.training_model_id))
    if pre_trainined_model is None:
        raise Exception
    # load the training data
    training_data = await load_data(account, pre_trainined_model)
    x_data, y_data = label_data(training_data)
    # create and train the model
    model = await train_model(x_data,y_data, pre_trainined_model, account)
    # upload the model to the database
    await upload_model_to_database(model, account, request.training_model_id)
    # set the status to complete
    account.models[request.training_model_id].training_state = TrainingState.COMPLETE
    await account.save()


@global_celery.task(name=Tasks.MODEL_TRAINING_TASK)
def model_training_task(request: str):
    '''Train a new model'''
    print(request)
    asyncio.set_event_loop(asyncio.new_event_loop())
    request_obj = TrainModelRequest(**json.loads(request))
    asyncio.run(model_training(request_obj))

############# Processing Functions

async def load_data(mongo_account : MongoAccount, pre_trainined_model : MongoPreMadeModel):
    '''
    Load the training data from S3 storage and construct a numpy array using it
    The data needs to be converted from binary form to the correct format
    '''
    data : dict[str,list] = {}


    for gesture_id in pre_trainined_model.gestures:
        recordings = mongo_account.gestures[str(gesture_id)]
        # print(recordings)
        data[str(gesture_id)] = []
        # TODO work out why this is a dict
        for recording_filename in recordings.user_recordings:
            s3_object = s3.get_object(Bucket='recordings', Key=recording_filename)
            body = s3_object['Body']
            numpy_data = pickle.loads(body.read())
            data[str(gesture_id)].append(np.array(numpy_data))

    return data

def label_data(data : dict):
    x = []
    y = []
    for index, values in enumerate(data.values()):
        inputs = np.stack(values, axis=0)
        labels = np.array([index for _ in range(len(inputs))])
        y.append(labels)
        x.append(inputs)

    x,y =   np.concatenate(x, axis=0), np.concatenate(y, axis=0)
    print(x.shape, y.shape)
    return x,y



async def train_model(x_data, y_data, pre_trainined_model : MongoPreMadeModel, account : MongoAccount) -> tf.keras.Model:
    '''
    Train the model using the training data
    The model output dimensions need to be dictated by the number of gestures
    '''
    # TODO create and train the model
    s3_folder = pre_trainined_model.model_weights
    bucket = s3_resource.Bucket('models')
    local_dir = f'/tmp/{account.models[str(pre_trainined_model.id)].model_location}'
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

    model = load_model(local_dir)
    history = model.fit(x_data, y_data, epochs=EPOCH_NUMS, batch_size=5, shuffle=True)
    return model
    # Load the model from the database
    # Fine tune the model on the x and y data



async def upload_model_to_database(model: tf.keras.Model,account: MongoAccount,  model_id):
    '''Upload the trained model file to the database'''
    local_folder = f'/tmp/{account.models[model_id].model_location}'
    model.save(local_folder)
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = os.path.join(account.models[model_id].model_location, os.path.relpath(local_path, local_folder))
            s3.upload_file(local_path, 'models', s3_path)

def load_model(model_file_path : str):
    model = tf.keras.models.load_model(model_file_path)
    print(model.summary())
    return model
