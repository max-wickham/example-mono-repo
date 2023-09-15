'''App entry point'''
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
from redis.asyncio import from_url
import redis
import boto3
import motor
from beanie import init_beanie

from schemas.mongo_models.account_models import MongoAccount
from schemas.mongo_models.training_models import MongoTrainingModel, TrainingState
from schemas.mongo_models.pre_made_models import MongoPreMadeModel
from schemas.mongo_models.gesture import MongoGestureInformation

from app.api.configs.configs import Config, environmentSettings


redis = from_url(environmentSettings.REDIS_URL, decode_responses=True)

app = FastAPI(
    title=Config.application_name
)

origins = [
    "http://localhost",
    "https://dashboard-deploy-h3gpr.ondigitalocean.app",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if environmentSettings.ENV == 'DEV':
    import os
    os.environ['S3_USE_SIGV4'] = 'True'
    s3 = boto3.resource('s3',
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

@app.get('/')
def docs():
    '''Redirect to docs'''
    return RedirectResponse('/docs')

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )


@app.on_event("startup")
async def app_init():
    '''App start up code'''
    client = motor.motor_asyncio.AsyncIOMotorClient(environmentSettings.mongo_database_url)
    await init_beanie(
        database=client['test']
        if environmentSettings.ENV == 'DEV'
        else client['main'],
        document_models=[MongoAccount, MongoTrainingModel, MongoPreMadeModel, MongoGestureInformation])

# import routes

from app.api.routes.inference_routes import *
from app.api.routes.recording_routes import *
# import app.api.routes.recording_routes

# from asyncio import sleep
# from sanic import Sanic

# app = Sanic("websocket")

# NUM_CHANNELS = 16
# FLOAT_LENGTH = 4


# @app.websocket("/sample")
# async def test(_, ws):
#     print('Connected')
#     count = 0
#     while True:
#         data = await ws.recv()
#         # print(data)
#         # Loop through the input_bytes and split into subarrays
#         sub_arrays = []
#         for i in range(0, len(data), NUM_CHANNELS*FLOAT_LENGTH):
#             subarray = data[i:i + NUM_CHANNELS*FLOAT_LENGTH]
#             sub_arrays.append(subarray)

#         for sub_array in sub_arrays:


#         count += 1
#         if count % 1000 == 0:
#             print(count)

# if __name__ == "__main__":
#     app.run(host="165.22.123.190", port=8005)
