/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Information to create a new pre made model
 */
export type PreMadeModelRequest = {
    name: string;
    gestures: Array<string>;
    model_weights: string;
    sample_period_s: number;
    sample_number: number;
    sample_frequency_hz: number;
    has_rest_class: boolean;
    num_channels: number;
};

