/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_get_token_token_post } from '../models/Body_get_token_token_post';
import type { Token } from '../models/Token';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class TokenService {

    /**
     * Get Token
     * Returns an auth token for an account login
     * @param formData
     * @returns Token Successful Response
     * @throws ApiError
     */
    public static getTokenTokenPost(
        formData: Body_get_token_token_post,
    ): CancelablePromise<Token> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/token',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Validate Token
     * Validates a token
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getValidateTokenValidateTokenGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/validate_token',
        });
    }

}
