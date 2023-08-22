'''Create a fake account and gestures'''
import asyncio
import requests
import os
import time

from passlib.context import CryptContext
from beanie import init_beanie
import motor

from schemas.mongo_models.account_models import MongoAccount, MongoAccountGestureRecordings
from schemas.mongo_models.gesture import MongoGestureInformation, MongoAccountGestureRecordings
from schemas.mongo_models.training_models import MongoTrainingModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# connect to mongo
async def main():
    '''Entrypoint'''
    time.sleep(3)
    client = motor.motor_asyncio.AsyncIOMotorClient(
        'mongodb://mongo:27017/')
    client.drop_database('test')
    await init_beanie(
        database=client['test'], document_models=[
            MongoAccount,
            MongoGestureInformation,
            # MongoAccountGestureRecordings,
            MongoTrainingModel
        ])

    mongo_account = MongoAccount(
        name='test',
        email='test',
        password_hash=pwd_context.hash('test'),
        gestures={},
        models=[]
    )
    await mongo_account.save()

    gesture = []
    for name in ('test_gesture', 'test_gesture2'):
        mongo_gesture = MongoGestureInformation(
            name=name,
            comments='comments',
            video_link='na',
            photo_link='na'
        )

        await mongo_gesture.save()
        gesture.append(mongo_gesture)

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


asyncio.run(main())
