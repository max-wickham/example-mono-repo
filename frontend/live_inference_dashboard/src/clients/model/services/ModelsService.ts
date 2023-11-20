/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PreMadeModelRequest } from '../models/PreMadeModelRequest';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ModelsService {

    /**
     * Post Model
     * Create a new user model from a model template
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static postModelModelModelIdPost(
        modelId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/model/{model_id}',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Del Model
     * Delete an existing model
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static delModelModelModelIdDelete(
        modelId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/model/{model_id}',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Post Pre Made Model
     * Create a new model template
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static postPreMadeModelPreMadeModelPost(
        requestBody: PreMadeModelRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/pre_made_model',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
