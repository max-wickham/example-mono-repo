import asyncio
import json
import random
import pickle
import string
import os
import time


from fastapi import WebSocket, WebSocketDisconnect
from beanie import PydanticObjectId
import numpy as np
import tensorflow as tf

from schemas.mongo_models.account_models import MongoAccount, TrainingState
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.pre_made_models import MongoPreMadeModel

from app.api.main import app, redis, s3, s3_client
from app.api.tools.tools import data_to_numpy

TIME_TO_HALF_RMS_S = 2


def load_model(model_file_path : str):
    model = tf.keras.models.load_model(model_file_path)
    print(model.summary())
    return model

def make_prediction(model: tf.keras.Model, data, num_channels: int, num_readings_per_inference: int):
    data = np.reshape(data, (1,num_readings_per_inference,num_channels))
    prediction = model(data)
    return prediction


def real_time_rms(data):
    return np.mean(np.sqrt(np.mean(np.array(data)**2, axis=-1)))



async def load_rest_data(mongo_account : MongoAccount, pre_trainined_model : MongoPreMadeModel):
    '''
    Load the training data from S3 storage and construct a numpy array using it
    The data needs to be converted from binary form to the correct format
    '''
    data = []


    for location in mongo_account.models[str(pre_trainined_model.id)].rest_data_file_locations:
        # print(recordings)
        s3_object = s3_client.get_object(Bucket='recordings', Key=location)
        body = s3_object['Body']
        numpy_data = pickle.loads(body.read())
        data.append(np.array(numpy_data))

    return np.array(data)


# TODO authentication
@app.websocket("/inference/{session_id}/{model_id}/{email}/{password}")
async def websocket_endpoint(websocket: WebSocket, session_id: int, model_id: str, email: str, password: str):
    '''Inference Websocket'''
    await websocket.accept()

    ########## Load Account Information
    mongo_account : MongoAccount | None = await MongoAccount.find(
        MongoAccount.email == email).first_or_none()
    # TODO assert that the password is correct
    assert mongo_account is not None

    ########## Load Model Information
    pre_trained_model : MongoPreMadeModel | None = await MongoPreMadeModel.get(
        PydanticObjectId(model_id))
    assert pre_trained_model is not None
    gestures : list[MongoGestureInformation | None] = [
        await MongoGestureInformation.get(gesture_id) for gesture_id in pre_trained_model.gestures]
    for gesture in gestures:
        assert gesture is not None
    model_info = mongo_account.models[model_id]
    assert model_info.training_state == TrainingState.COMPLETE
    num_readings_per_inference = pre_trained_model.sample_number

    ########## Download Model
    # TODO use tmp library
    s3_folder = model_info.model_location
    bucket = s3.Bucket('models')
    local_dir = f'/tmp/{"".join(random.choices(string.ascii_uppercase + string.digits, k=10))}'
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        print(obj.key)
        bucket.download_file(obj.key, target)

    ########## Construct Model
    model = load_model(local_dir)

    ########## Load Inference Data
    data_length = await redis.llen(str(session_id))
    while data_length < 1.2*num_readings_per_inference:
        data_length = await redis.llen(str(session_id))
        await asyncio.sleep(0.1)
    data = await redis.lrange(str(session_id), data_length-num_readings_per_inference, -1)
    data = data_to_numpy(data)

    data_length = await redis.llen(str(session_id))
    saved = []
    baseline_rms = real_time_rms(data)
    rms_frac = 0.06
    rms_time = time.time()



    rest_data = await load_rest_data(mongo_account, pre_trained_model)
    baseline_rms = real_time_rms(rest_data)

    while True:
        try:
            data_length = await redis.llen(str(session_id))
            data = await redis.lrange(str(session_id), data_length-num_readings_per_inference, -1)
            data = np.array(data_to_numpy(data))
            print(data[-1])
            saved.append(data)
            # if len(saved) % 20 == 0:
            save_data = np.vstack(saved)
            with open('/app/api/data.pkl', 'wb') as file:
                pickle.dump(save_data, file)
            saved = saved[-20:]
                # saved = []

            ########## Run inference
            result = 'Rest'
            # print('RMS', baseline_rms, real_time_rms(data))
            if real_time_rms(data) > 1.1 * baseline_rms:
                inference = make_prediction(model, data, pre_trained_model.num_channels, num_readings_per_inference)
                print('inference',inference.numpy()[0])
                if tf.reduce_max(inference).numpy() > 0.99:
                    max_index = int(np.argmax(inference.numpy()[0]))
                    if max_index >= len(gestures):
                        result = 'Rest'
                    else:
                        gesture = gestures[max_index]
                        assert gesture is not None
                        result = gesture.name
            else:
                ########## Update baseline rms
                rms_period = time.time() - rms_time
                rms_time = time.time()
                # baseline_rms = real_time_rms(data) * rms_frac + (1-rms_frac) * baseline_rms
                rms_frac = 1 - np.power(1 / 2, 1 / (TIME_TO_HALF_RMS_S / rms_period))

            await websocket.send_text(json.dumps({
                "inference":result,
            }))
        except Exception as e:
            await websocket.send_text(json.dumps({
                "inference":"Error",
            }))
        await asyncio.sleep(0.05)
