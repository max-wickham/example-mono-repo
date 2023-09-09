/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ModelsService {

    /**
     * Post Model
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

}
