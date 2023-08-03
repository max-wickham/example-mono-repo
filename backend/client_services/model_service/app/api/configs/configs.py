'''Application configs'''

from pydantic import BaseSettings

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
    S3_REGION : str = "ams3"
    S3_URL : str = "http://10.5.10.6:9000"
    S3_KEY : str = "56qHNcBwWOZSULWDUWaFNNm3AUNmU2UglcyHWECQ"
    S3_ID : str = "8NXWLDpiLeuKWhM1XQ5k"

environmentSettings = EnvironmentSettings()

class Config:
    '''None secret configs'''
    application_name : str = "model-service"
    version = "0.0.1"
