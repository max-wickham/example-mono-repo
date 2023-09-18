/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PreMadeModels } from '../models/PreMadeModels';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class PreMadeModelsService {

    /**
     * Get Pre Made Models
     * Get a list of the pre made models
     * @returns PreMadeModels Successful Response
     * @throws ApiError
     */
    public static getPreMadeModelsPreMadeModelsGet(): CancelablePromise<PreMadeModels> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/pre_made_models',
        });
    }

}
