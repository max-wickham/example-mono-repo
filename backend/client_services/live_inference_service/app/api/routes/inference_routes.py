import asyncio
import base64
import json
import struct
import random
import pickle

import string
import os
from app.api.routes.feature_extraction import real_time_feature_extraction
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.pre_made_models import MongoPreMadeModel

from fastapi import WebSocket
from fastapi.params import Depends
from beanie import PydanticObjectId
import numpy as np
import tensorflow as tf

from libs.authentication.user_token_auth import TokenData, token_authentication
from schemas.mongo_models.account_models import MongoAccount, TrainingState

from app.api.main import app, redis, s3
from app.api.tools.tools import data_to_numpy

NUM_CHANNELS = 8
INFERENCE_PERIOD = 0.5
NUM_READINGS = 500

# def data_to_numpy(data: list[bytes]):
#     # print(data[0])
#     return np.array([struct.unpack(f'{NUM_CHANNELS}f', base64.b64decode(reading_set.encode('utf8'))) for reading_set in data])


def load_model(model_file_path : str):
    model = tf.keras.models.load_model(model_file_path)
    print(model.summary())
    return model

def make_prediction(model: tf.keras.Model, data):
    # data = data.flatten()
    # TODO may need to add dimension
    # print('Making Prediction')
    # data = real_time_feature_extraction(data)
    # 8 * 500, sample frequency, 80

    # extract_all_features(data,)
    data = np.reshape(data, (1,NUM_READINGS,NUM_CHANNELS))
    prediction = model(data)
    # print(f'Prediction: {prediction}')
    return prediction


def real_time_rms(data):
    return np.mean(np.sqrt(np.mean((data)**2, axis=-1)))


count = 0


# TODO authentication
@app.websocket("/inference/{session_id}/{model_id}/{email}/{password}")
async def websocket_endpoint(websocket: WebSocket, session_id: int, model_id: str, email: str, password: str):
    global count
    await websocket.accept()
    baseline_rms = 1
    # TODO dependent on time between readings
    rms_frac = 0.06
    ########## Load Account Information
    print(email)
    mongo_account : MongoAccount = await MongoAccount.find(MongoAccount.email == email).first_or_none()
    if mongo_account is None:
        raise Exception
    pre_trained_model = await MongoPreMadeModel.get(PydanticObjectId(model_id))
    gestures = [await MongoGestureInformation.get(gesture_id) for gesture_id in pre_trained_model.gestures]
    model_info = mongo_account.models[model_id]
    print(model_info)
    assert model_info.training_state == TrainingState.COMPLETE


    # s3_object = s3.get_object(Bucket='models', Key=mongo_training_model.model_file_name)

    ########## Download Model
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

    data_length = await redis.llen(str(session_id))
    while data_length < 1.2*NUM_READINGS:
        data_length = await redis.llen(str(session_id))
        # print(data_length)
        await asyncio.sleep(0.1)
    data = await redis.lrange(str(session_id), data_length-NUM_READINGS, -1)
    data = data_to_numpy(data)

    # while True:
    #     # print(data_length)
    #     new_data = await redis.lrange(str(session_id), data_length, -1)
    #     current_data_length = await redis.llen(str(session_id))
    #     if current_data_length < data_length:
    #         new_data = await redis.lrange(str(session_id), -1*NUM_READINGS, -1)
    #     new_length = len(new_data)
    #     if new_length > 0 or current_data_length < data_length:
    #         data_length = current_data_length
    #         # print(new_length)
    #         print(new_data[0])
    #         new_data = data_to_numpy(new_data)
    #         data = np.vstack((data, new_data))
    #         data = data[-1*NUM_READINGS:]
    #         print(data[-1])
    #         baseline_rms = real_time_rms(data) * rms_frac + (1-rms_frac) * baseline_rms
    #         # TODO run inference
    #         # try:
    #         result = 'Rest'
    #         print('RMS', baseline_rms, real_time_rms(data))
    #         if real_time_rms(data) > 1.1 * baseline_rms or True:
    #             inference = make_prediction(model, data)
    #             print(inference.numpy()[0])
    #             if tf.reduce_max(inference).numpy() > 0.99:
    #                 max_index = np.argmax(inference.numpy()[0])
    #                 result = gestures[max_index].name

    #         # except:
    #         #     count += 1
    #         #     inference = f"NA {count}"

    #         await websocket.send_text(json.dumps({
    #             "inference":result,
    #         }))
    #         await asyncio.sleep(0.05)

    data_length = await redis.llen(str(session_id))
    saved = []

    while True:
        new_data_length = await redis.llen(str(session_id))
        if new_data_length - data_length > 250:
            data_length = await redis.llen(str(session_id))
            data = await redis.lrange(str(session_id), data_length-NUM_READINGS, -1)
            data = np.array(data_to_numpy(data))
            print(data[-1])
            saved.append(data)
            # if len(saved) % 20 == 0:
            save_data = np.vstack(saved)
            with open('/app/api/data.pkl', 'wb') as file:
                pickle.dump(save_data, file)
            saved = saved[-20:]
                # saved = []

            baseline_rms = real_time_rms(data) * rms_frac + (1-rms_frac) * baseline_rms
            # TODO run inference
            # try:
            result = 'Rest'
            print('RMS', baseline_rms, real_time_rms(data))
            if real_time_rms(data) > 1.1 * baseline_rms:
                inference = make_prediction(model, data)
                print(inference.numpy()[0])
                if tf.reduce_max(inference).numpy() > 0.99:
                    max_index = np.argmax(inference.numpy()[0])
                    result = gestures[max_index].name

            # except:
            #     count += 1
            #     inference = f"NA {count}"

            await websocket.send_text(json.dumps({
                "inference":result,
            }))
        await asyncio.sleep(0.05)
