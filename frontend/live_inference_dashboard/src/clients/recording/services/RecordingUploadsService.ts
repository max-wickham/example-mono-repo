/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_post_recording_recording__gesture_id__post } from '../models/Body_post_recording_recording__gesture_id__post';
import type { Body_post_rest_recording_rest_recording__model_id__post } from '../models/Body_post_rest_recording_rest_recording__model_id__post';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecordingUploadsService {

    /**
     * Post Recording
     * Upload a binary recording file of the sensor data
     * @param gestureId
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static postRecordingRecordingGestureIdPost(
        gestureId: string,
        formData: Body_post_recording_recording__gesture_id__post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/recording/{gesture_id}',
            path: {
                'gesture_id': gestureId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Post Rest Recording
     * Upload a binary recording file of the sensor data as rest data for a model
     * @param modelId
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static postRestRecordingRestRecordingModelIdPost(
        modelId: string,
        formData: Body_post_rest_recording_rest_recording__model_id__post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/rest_recording/{model_id}',
            path: {
                'model_id': modelId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
