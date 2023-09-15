'''App entry point'''
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
import motor
from beanie import init_beanie


from schemas.mongo_models.account_models import MongoAccount
from app.api.configs.configs import Config, environmentSettings


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
    # if environmentSettings.ENV == 'DEV':
    #     await client.drop_database('test')
    await init_beanie(
        database=client['test']
        if environmentSettings.ENV == 'DEV'
        else client['main'],
        document_models=[MongoAccount])
    # if environmentSettings.ENV == 'DEV':
    #     from app.api.authentication.authentication import get_password_hash
    #     mongo_account = MongoAccount(
    #         name = 'test',
    #         email='test',
    #         password_hash=get_password_hash('test')
    #     )
    #     await mongo_account.save()


# import routes

from app.api.routes.account_routes import *
from app.api.routes.authentication_routes import *
