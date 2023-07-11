'''App entry point'''
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
import motor
from beanie import init_beanie
from redis.asyncio import from_url

from app.api.configs.configs import Config, EnvironmentSettings


app = FastAPI(
    title=Config.application_name
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
)
print(EnvironmentSettings.REDIS_URL)
redis = from_url('redis://redis:6379', decode_responses=True)


@app.get('/')
def docs():
    '''Redirect to docs'''
    return RedirectResponse('/docs')

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req):
    '''Provides swagger documentation'''
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )

@app.on_event("startup")
async def app_init():
    '''App start up code'''
    client = motor.motor_asyncio.AsyncIOMotorClient(EnvironmentSettings.MONGO_DATABASE_URL)
    await init_beanie(
        database=client['test']
        if EnvironmentSettings.ENV == 'DEV'
        else client['main'],
        document_models=[])


from app.api.sockets.ingest_sockets import *
