'''Create a fake account and gestures'''
import asyncio
import requests
import os
import base64
import struct
import time
import pickle

from passlib.context import CryptContext
from beanie import init_beanie
import motor
import boto3
from redis.asyncio import from_url

from schemas.mongo_models.account_models import MongoAccount, UserFineTunedModel, TrainingState
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.pre_made_models import MongoPreMadeModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis = from_url("redis://redis", decode_responses=True)

import os
os.environ['S3_USE_SIGV4'] = 'True'
s3 = boto3.resource('s3',
                    endpoint_url="http://10.5.10.6:9000",
                    aws_access_key_id="y2GJYMfN9Ia7flEROuT8",
                    aws_secret_access_key="YWbbvo218D5DSijDf3moSUSt9M4n6BAmxcqs4Ahg"
                    )

def read_from_pickle(path):
    with open(path, 'rb') as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass

# connect to mongo
async def main():
    '''Entrypoint'''
    time.sleep(3)
    client = motor.motor_asyncio.AsyncIOMotorClient(
        os.environ['MONGO_DATABASE_URL'])
    # client.drop_database('test')
    await init_beanie(
        database=client['test'], document_models=[
            MongoGestureInformation,
            MongoAccount,
            MongoPreMadeModel
        ])

    # mongo_account = MongoAccount(
    #     name='Matteo',
    #     email='mtt.pzz56@gmail.com',
    #     password_hash=pwd_context.hash('test'),
    #     gestures={},
    #     models={}
    # )
    # await mongo_account.save()

    # gestures = []
    # gesture_name = ['Hold Right','Hold Left','Hold Up','Hold Down']
    # for name in gesture_name:
    #     mongo_gesture = MongoGestureInformation(
    #         name=name,
    #         comments='comments',
    #         video_link='na',
    #         photo_link='na',
    #         continuous=True
    #     )

    #     await mongo_gesture.save()
    #     gestures.append(mongo_gesture)


    # mongo_gesture = MongoGestureInformation(
    #         name='Click',
    #         comments='comments',
    #         video_link='na',
    #         photo_link='na',
    #         continuous=False
    #     )

    # await mongo_gesture.save()
    # gestures.append(mongo_gesture)

    # pre_made_model = MongoPreMadeModel(
    #     name = 'Mouse',
    #     gestures = [gesture.id for gesture in gestures],
    #     model_weights = 'mouse_model',
    #     sample_period_s=0.25
    # )

    # await pre_made_model.save()

    # pre_made_model = MongoPreMadeModel(
    #     name = 'Penguin Game',
    #     gestures = [gesture.id for gesture in gestures[:2]],
    #     model_weights = 'penguin_model',
    #     sample_period_s=0.25
    # )

    # await pre_made_model.save()


    # pre_made_model = MongoPreMadeModel(
    #     name = 'Mouse Rest',
    #     gestures = [gesture.id for gesture in gestures],
    #     model_weights = 'trackpad_rest',
    #     sample_period_s=0.25,
    #     has_rest_class=True,
    # )

    # await pre_made_model.save()

    # pre_made_model = MongoPreMadeModel(
    #     name = 'Penguin Game Rest',
    #     gestures = [gesture.id for gesture in gestures[:2]],
    #     model_weights = 'penguin_rest',
    #     sample_period_s=0.25,
    #     has_rest_class=True,
    # )

    # await pre_made_model.save()


    # mongo_gesture = MongoGestureInformation(
    #     name='Pinch',
    #     comments='comments',
    #     video_link='na',
    #     photo_link='na',
    #     continuous=True
    # )

    # await mongo_gesture.save()


    # pre_made_model = MongoPreMadeModel(
    #     name = 'Pinch Model',
    #     gestures = [mongo_gesture.id],
    #     model_weights = 'pinch_rest_2000',
    #     sample_period_s=1,
    #     num_samples_per_recording=2000,
    #     has_rest_class=True,
    # )

    # await pre_made_model.save()


    # #########################################

    # gestures = []
    # gesture_name = ['Hold Right 116','Hold Left 16','Hold Up 16','Hold Down 16']
    # for name in gesture_name:
    #     mongo_gesture = MongoGestureInformation(
    #         name=name,
    #         comments='comments',
    #         video_link='na',
    #         photo_link='na',
    #         continuous=True,
    #         num_channels=16,
    #     )

    #     await mongo_gesture.save()
    #     gestures.append(mongo_gesture)


    # mongo_gesture = MongoGestureInformation(
    #         name='Click 16',
    #         comments='comments',
    #         video_link='na',
    #         photo_link='na',
    #         continuous=False,
    #         num_channels=16,
    #     )

    # await mongo_gesture.save()
    # gestures.append(mongo_gesture)

    # pre_made_model = MongoPreMadeModel(
    #     name = 'Penguin Game 16',
    #     gestures = [gesture.id for gesture in gestures[:2]],
    #     model_weights = 'penguin_16',
    #     sample_period_s=0.25,
    #     has_rest_class=True,
    #     num_channels=16,
    # )

    # await pre_made_model.save()

    # pre_made_model = MongoPreMadeModel(
    #     name = 'Mouse 16',
    #     gestures = [gesture.id for gesture in gestures],
    #     model_weights = 'trackpad_16',
    #     sample_period_s=0.25,
    #     has_rest_class=True,
    #     num_channels=16,
    # )

    # await pre_made_model.save()


    # #############################

    # gestures = []
    # gesture_name = ['Hold Right 16 2K','Hold Left 16 2K','Hold Up 16 2K','Hold Down 16 2K']
    # for name in gesture_name:
    #     mongo_gesture = MongoGestureInformation(
    #         name=name,
    #         comments='comments',
    #         video_link='na',
    #         photo_link='na',
    #         continuous=True,
    #         num_channels=16,
    #         sampling_frequency_hz=2000,
    #     )

    #     await mongo_gesture.save()
    #     gestures.append(mongo_gesture)

    # pre_made_model = MongoPreMadeModel(
    #     name = 'Penguin Game 16 2000',
    #     gestures = [gesture.id for gesture in gestures[:2]],
    #     model_weights = 'penguin_16',
    #     sample_period_s=0.25,
    #     sample_number= 500,
    #     has_rest_class=True,
    #     sample_frequency_hz=2000,
    #     num_channels=16,
    # )

    # await pre_made_model.save()

    # gestures = []
    # gesture_name = ['Swipe Right', 'Swipe Left']
    # for name in gesture_name:
    #     mongo_gesture = MongoGestureInformation(
    #         name=name,
    #         comments='comments',
    #         video_link='na',
    #         photo_link='na',
    #         continuous=False
    #     )

    #     await mongo_gesture.save()
    #     gestures.append(mongo_gesture)

    # mongo_account.models[str(pre_made_model.id)] = UserFineTunedModel(
    #     name = 'Na',
    #     training_state = TrainingState.COMPLETE,
    #     model_location = 'model_saving',
    #     pre_made_model_id = pre_made_model.id,
    # )


    # mongo_account.models[str(pre_made_model.id)] = UserFineTunedModel(
    #     name = 'Na',
    #     training_state = TrainingState.COMPLETE,
    #     model_location = 'model_saving',
    #     pre_made_model_id = pre_made_model.id,
    # )

    # await mongo_account.save();





    # mongo_training_model = MongoTrainingModel(
    #     creation_date = time.time(),
    #     name = 'test_model',
    #     gestures = [MongoTrainingModel.MongoModelGestureInfo(
    #         gesture_name= gesture.name,
    #         video_link = '',
    #         photo_link = '',
    #         gesture_id = str(gesture.id),
    #         command = ''
    #     ) for gesture in gestures],
    #     training_state = TrainingState.COMPLETE,
    #     account_id = mongo_account.id,
    #     model_file_name = 'model_saving',
    #     pre_made_model_id=pre_made_model.id
    # )
    # await mongo_training_model.save()
    # mongo_account.models.append(str(mongo_training_model.id))
    # await mongo_account.save()


    # mongo_training_model = MongoTrainingModel(
    #     creation_date = time.time(),
    #     name = 'test_model2',
    #     gestures = [MongoTrainingModel.MongoModelGestureInfo(
    #         gesture_name= gesture.name,
    #         video_link = '',
    #         photo_link = '',
    #         gesture_id = str(gesture.id),
    #         command = ''
    #     ) for gesture in gestures],
    #     training_state = TrainingState.COMPLETE,
    #     account_id = mongo_account.id,
    #     model_file_name = 'model_saving',
    #     pre_made_model_id=pre_made_model.id
    # )
    # await mongo_training_model.save()
    # mongo_account.models.append(str(mongo_training_model.id))
    # await mongo_account.save()

    # print(mongo_training_model.id)

    # TODO upload model file

    # bucket_name = 'models'

    # # Specify the local folder path you want to upload
    # local_folder_path = '/model_saving'

    # # Walk through the local folder and upload each file to S3
    # for root, dirs, files in os.walk(local_folder_path):
    #     for file in files:
    #         local_file_path = os.path.join(root, file)
    #         # Construct the S3 object key by removing the local folder path
    #         s3_object_key = os.path.relpath(local_file_path, local_folder_path)

    #         # Upload the file to S3
    #         s3.upload_file(local_file_path, bucket_name, s3_object_key)



######################################

    gestures = []
    gesture_name = ['Left Finger 16 2K','Right Finger 16 2K']
    for name in gesture_name:
        mongo_gesture = MongoGestureInformation(
            name=name,
            comments='comments',
            video_link='na',
            photo_link='na',
            continuous=True,
            num_channels=16,
            sampling_frequency_hz=2000,
        )

        await mongo_gesture.save()
        gestures.append(mongo_gesture)

    pre_made_model = MongoPreMadeModel(
        name = 'Left Right Finger 16 2000',
        gestures = [gesture.id for gesture in gestures[:2]],
        model_weights = 'penguin_16',
        sample_period_s=0.25,
        sample_number= 500,
        has_rest_class=True,
        sample_frequency_hz=2000,
        num_channels=16,
    )

    await pre_made_model.save()

    ############################



    # response = requests.post(
    #     'http://account-service:8080/token',
    #     data={
    #         'username': 'test',
    #         'password': 'test'
    #     }, timeout=3)
    # token = 'Bearer ' + response.json()['access_token']
    # print(token)
    # response = requests.get(
    #     'http://recording-upload-service:8080/gestures',
    #     headers={'Authorization': token},
    #     timeout=3)
    # gestures = response.json()
    # print(gestures)
    # gesture_id = list(gestures['gestures'].keys())[0]
    # print(gesture_id)

    # with open('/requirements.txt','rb') as file:
    #     response = requests.post(
    #         f'http://recording-upload-service:8080/recording/{gesture_id}',
    #         headers={'Authorization': token},
    #         files={'recording':file.read()},
    #         timeout=3)
    #     print(response.json())
    # response = requests.post(
    #     'http://model-service:8080/model',
    #     headers={'Authorization': token},
    #     json={
    #         "gestures": [
    #             {
    #                 "gesture_id": gesture_id,
    #                 "command": "CtrlC"
    #             }
    #         ],
    #         "model_name": "model1"
    #     },
    #     timeout=3)
    # print('loading data')
    # data = read_from_pickle('/X_test.pkl')
    # print(data.shape)

    NUM_FEATURES = 16
    FREQUENCY = 1000
    MAX_LENGTH = 100000
    SESSION_ID = 201326592
    BYTES_PER_INT = 3

    await redis.delete(str(SESSION_ID))
    while True:
        int_array = [int(i) for i in range(NUM_FEATURES)]
        byte_array = bytearray()
        # Iterate through the float values and pack them as float32 (4 bytes each)
        for value in int_array:
            packed_value = value.to_bytes(BYTES_PER_INT, byteorder='big', signed=True)
            byte_array.extend(packed_value)

        base64_encoded = base64.b64encode(byte_array)
        base64_encoded_str = base64_encoded.decode('utf-8')
        await redis.lpush(str(SESSION_ID), base64_encoded_str)
        await redis.set(f'{SESSION_ID}_CHANNEL_COUNT', NUM_FEATURES)
        await redis.set(f'{SESSION_ID}_FREQUENCY_HZ', FREQUENCY)
        time.sleep(1 / FREQUENCY)
        length = await redis.llen(str(SESSION_ID))
        if length > MAX_LENGTH:
            await redis.ltrim(str(SESSION_ID), int(length / 2), length)



asyncio.run(main())
