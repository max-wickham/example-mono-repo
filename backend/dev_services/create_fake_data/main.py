'''Create a fake account and gestures'''
import asyncio

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

    client = motor.motor_asyncio.AsyncIOMotorClient(
        'mongodb://mongo:27017/')
    client.drop_database('test')
    await init_beanie(
        database=client['test'], document_models=[
            MongoAccount,
            MongoAccountGestureRecordings,
            MongoGestureInformation,
            MongoAccountGestureRecordings,
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




asyncio.run(main())
