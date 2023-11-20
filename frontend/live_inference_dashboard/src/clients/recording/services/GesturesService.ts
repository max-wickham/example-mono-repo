/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GesturesService {

    /**
     * Get Recording Files
     * Returns back a zip file with all the recordings for the user and gesture
     * @param gestureId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRecordingFilesRecordingFilesGestureIdGet(
        gestureId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/recording_files/{gesture_id}',
            path: {
                'gesture_id': gestureId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
