/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Gestures } from '../models/Gestures';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GestureInfoService {

    /**
     * Get Gestures
     * Upload a binary recording file of the sensor data
     * @returns Gestures Successful Response
     * @throws ApiError
     */
    public static getGesturesGesturesGet(): CancelablePromise<Gestures> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/gestures',
        });
    }

    /**
     * Delete Gesture Recordings
     * Upload a binary recording file of the sensor data
     * @param gestureId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteGestureRecordingsGesutureRecordingsGestureIdDelete(
        gestureId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/gesuture_recordings/{gesture_id}',
            path: {
                'gesture_id': gestureId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Rest Recordings
     * Upload a binary recording file of the sensor data
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteRestRecordingsRestRecordingsModelIdDelete(
        modelId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/rest_recordings/{model_id}',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
