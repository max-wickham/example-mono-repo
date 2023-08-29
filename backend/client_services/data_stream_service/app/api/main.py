'''App entry point'''
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware
from redis.asyncio import from_url
import redis
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

# import routes

from app.api.routes.data_stream_routes import *


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
