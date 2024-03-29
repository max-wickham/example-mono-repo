/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class StreamInfoService {

    /**
     * Get Stream Active
     * @param streamId
     * @returns boolean Successful Response
     * @throws ApiError
     */
    public static getStreamActiveStreamActiveStreamIdGet(
        streamId: string,
    ): CancelablePromise<boolean> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/stream_active/{stream_id}',
            path: {
                'stream_id': streamId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Stream Channel Count
     * @param streamId
     * @returns number Successful Response
     * @throws ApiError
     */
    public static getStreamChannelCountStreamChannelCountStreamIdGet(
        streamId: string,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/stream_channel_count/{stream_id}',
            path: {
                'stream_id': streamId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Stream Frequency
     * @param streamId
     * @returns number Successful Response
     * @throws ApiError
     */
    public static getStreamFrequencyStreamFrequencyStreamIdGet(
        streamId: string,
    ): CancelablePromise<number> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/stream_frequency/{stream_id}',
            path: {
                'stream_id': streamId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
