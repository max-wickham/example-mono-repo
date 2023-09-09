/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class RecordingStreamingService {

    /**
     * Get Save Recording
     * Take the last 0.5 seconds of recording data, download it and send it to the recording upload service
     * @param sessionId
     * @param gestureId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getSaveRecordingSaveRecordingSessionIdGestureIdGet(
        sessionId: string,
        gestureId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/save_recording/{session_id}/{gesture_id}',
            path: {
                'session_id': sessionId,
                'gesture_id': gestureId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
