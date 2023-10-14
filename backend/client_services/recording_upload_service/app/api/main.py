'''App entry point'''
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from celery import Celery
from starlette.middleware.cors import CORSMiddleware
import motor
from beanie import init_beanie
import boto3

from schemas.mongo_models.account_models import MongoAccount
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.pre_made_models import MongoPreMadeModel
from app.api.configs import Config, environmentSettings


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

celery = Celery(__name__)
celery.conf.broker_url = environmentSettings.CELERY_BROKER_URL
celery.conf.result_backend = environmentSettings.CELERY_RESULT_BACKEND


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
    s3_resource = boto3.resource('s3',
                      endpoint_url=environmentSettings.S3_URL,
                      aws_access_key_id=environmentSettings.S3_ID,
                      aws_secret_access_key=environmentSettings.S3_KEY
                      )

# check if bucket already exists
try:
    s3.create_bucket(Bucket='processed-recordings')
    s3.create_bucket(Bucket='recordings')
except Exception:
    print('unable to create bucket')

@app.get('/')
def docs():
    '''Redirect to docs'''
    return RedirectResponse('/docs')

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url  # type: ignore
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )


@app.on_event("startup")
async def app_init():
    '''App start up code'''
    client = motor.motor_asyncio.AsyncIOMotorClient(environmentSettings.mongo_database_url)  # type: ignore
    await init_beanie(
        database=client['test']
        if environmentSettings.ENV == 'DEV'
        else client['main'],
        document_models=[MongoGestureInformation, MongoAccount,MongoPreMadeModel])  # type: ignore


# import routes

from app.api.routes.upload_routes import *
from app.api.routes.info_routes import *
