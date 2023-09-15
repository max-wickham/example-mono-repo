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

}
