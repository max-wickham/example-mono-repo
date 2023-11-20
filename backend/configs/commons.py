'''Configs common to multiple services'''



class Tasks:
    '''Names of cross service tasks'''

    GLOBAL_CELERY_SERVICE = 'tasks'
    MODEL_TRAINING_TASK = 'model_training_task'

class StreamingConfigs:
    '''Configs for receiving data from devices'''
    BYTES_PER_INT = 3
    MAX_BUFFER_LENGTH = 200000
