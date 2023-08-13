'''Messages required to trigger model training task'''

from pydantic import BaseModel


class TrainModelRequest(BaseModel):
    '''Request to train a new model with necessary parameters'''
    account_id : str
    training_model_id : str
