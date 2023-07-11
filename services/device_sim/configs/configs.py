'''Application configs'''

from pydantic import BaseSettings

class EnvironmentSettings(BaseSettings):
    '''Environment settings'''
    MONGO_DATABASE_URL : str = 'mongodb://localhost:27017/'
    REDIS_URL : str = 'redis://localhost'
    SOCKET_URL : str = 'ws://localhost:8000'

EnvironmentSettings = EnvironmentSettings()

class Config:
    '''None secret configs'''
    application_name : str = "data-ingest-service"
    version = "0.0.1"
    max_ingest_stream_length = 10000
