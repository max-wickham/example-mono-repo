'''Application configs'''

from pydantic_settings import BaseSettings

class EnvironmentSettings(BaseSettings):
    '''Environment settings'''
    secret : str = "secret"
    jwt_secret : str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    jwt_algorithm : str = "HS256"
    jwt_exp : int = 2*7*24*60*60
    token_url :str = "http:localhost:8000/token"
    mongo_database_url : str = 'mongodb://localhost:27017/'
    api_url : str = 'http://localhost:8000'
    ENV : str = ""
    REDIS_URL: str = "redis://localhost:6379"
    S3_REGION : str = "ams3"
    S3_URL : str = "http://10.5.10.6:9000"
    S3_KEY : str = "YWbbvo218D5DSijDf3moSUSt9M4n6BAmxcqs4Ahg"
    S3_ID : str = "y2GJYMfN9Ia7flEROuT8"
    CELERY_BROKER_URL : str = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND : str = "redis://localhost:6379"


environmentSettings = EnvironmentSettings()

class Config:
    '''None secret configs'''
    application_name : str = "data-stream-service"
    version = "0.0.1"
