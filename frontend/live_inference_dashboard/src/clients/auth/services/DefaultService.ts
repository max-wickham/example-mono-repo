/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccountInfo } from '../models/AccountInfo';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

    /**
     * Docs
     * Redirect to docs
     * @returns any Successful Response
     * @throws ApiError
     */
    public static docsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }

    /**
     * Get Accounts
     * Return the information regarding the current users account
     * @returns AccountInfo Successful Response
     * @throws ApiError
     */
    public static getAccountsAccountGet(): CancelablePromise<AccountInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/account',
        });
    }

}
