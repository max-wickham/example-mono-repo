import asyncio
import json
import random
import pickle
import string
import os
import time


from fastapi import WebSocket
from beanie import PydanticObjectId
import numpy as np
import tensorflow as tf

from schemas.mongo_models.account_models import MongoAccount, TrainingState
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.pre_made_models import MongoPreMadeModel

from app.api.main import app, redis, s3
from app.api.tools.tools import data_to_numpy

NUM_CHANNELS = 8
INFERENCE_PERIOD_S = 0.5
INFERENCE_FREQUENCY_HZ = 1000
NUM_READINGS_PER_INFERENCE = int(INFERENCE_FREQUENCY_HZ * INFERENCE_PERIOD_S)
# This is the time taken for the current rms value to account for half of the new rms value using exponentially weighted moving average
TIME_TO_HALF_RMS_S = 2


def load_model(model_file_path : str):
    model = tf.keras.models.load_model(model_file_path)
    print(model.summary())
    return model

def make_prediction(model: tf.keras.Model, data):
    data = np.reshape(data, (1,NUM_READINGS_PER_INFERENCE,NUM_CHANNELS))
    prediction = model(data)
    return prediction


def real_time_rms(data):
    return np.mean(np.sqrt(np.mean((data)**2, axis=-1)))


count = 0


# TODO authentication
@app.websocket("/inference/{session_id}/{model_id}/{email}/{password}")
async def websocket_endpoint(websocket: WebSocket, session_id: int, model_id: str, email: str, password: str):
    global count
    await websocket.accept()
    # TODO dependent on time between readings
    ########## Load Account Information
    print(email)
    mongo_account : MongoAccount | None = await MongoAccount.find(MongoAccount.email == email).first_or_none()
    if mongo_account is None:
        raise Exception
    pre_trained_model : MongoPreMadeModel | None = await MongoPreMadeModel.get(PydanticObjectId(model_id))
    if pre_trained_model is None:
        raise Exception
    gestures : list[MongoGestureInformation | None] = [await MongoGestureInformation.get(gesture_id) for gesture_id in pre_trained_model.gestures]
    for gesture in gestures:
        assert gesture is not None
    model_info = mongo_account.models[model_id]
    assert model_info.training_state == TrainingState.COMPLETE

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

    ########## Load Inference Data
    data_length = await redis.llen(str(session_id))
    while data_length < 1.2*NUM_READINGS_PER_INFERENCE:
        data_length = await redis.llen(str(session_id))
        await asyncio.sleep(0.1)
    data = await redis.lrange(str(session_id), data_length-NUM_READINGS_PER_INFERENCE, -1)
    data = data_to_numpy(data)

    data_length = await redis.llen(str(session_id))
    saved = []
    baseline_rms = real_time_rms(data)
    rms_frac = 0.06
    rms_time = time.time()

    while True:
        new_data_length = await redis.llen(str(session_id))

        if new_data_length - data_length > 250:
            data_length = await redis.llen(str(session_id))
            data = await redis.lrange(str(session_id), data_length-NUM_READINGS_PER_INFERENCE, -1)
            data = np.array(data_to_numpy(data))
            print(data[-1])
            saved.append(data)
            # if len(saved) % 20 == 0:
            save_data = np.vstack(saved)
            with open('/app/api/data.pkl', 'wb') as file:
                pickle.dump(save_data, file)
            saved = saved[-20:]
                # saved = []

            ########## Update baseline rms
            rms_period = time.time() - rms_time
            rms_time = time.time()
            baseline_rms = real_time_rms(data) * rms_frac + (1-rms_frac) * baseline_rms
            rms_frac = 1 - np.pow(1 / 2, 1 / (TIME_TO_HALF_RMS_S / rms_period))

            ########## Run inference
            result = 'Rest'
            # print('RMS', baseline_rms, real_time_rms(data))
            if real_time_rms(data) > 1.1 * baseline_rms:
                inference = make_prediction(model, data)
                print(inference.numpy()[0])
                if tf.reduce_max(inference).numpy() > 0.99:
                    max_index = np.argmax(inference.numpy()[0])
                    result = gestures[max_index].name

            await websocket.send_text(json.dumps({
                "inference":result,
            }))
        await asyncio.sleep(0.05)


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
