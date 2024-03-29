/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GestureRequest } from '../models/GestureRequest';
import type { Gestures } from '../models/Gestures';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GesturesService {

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
     * Post Gesture
     * Create a new gesture
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static postGestureGesturePost(
        requestBody: GestureRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/gesture',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Del Gesture
     * Delete an existing gesture globally
     * @param gestureId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static delGestureGestureGestureIdDelete(
        gestureId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/gesture/{gesture_id}',
            path: {
                'gesture_id': gestureId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
