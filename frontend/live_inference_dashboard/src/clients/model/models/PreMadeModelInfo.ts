/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GestureInfo } from './GestureInfo';
import type { TrainingState } from './TrainingState';

/**
 * Description of a model that can be deployed to a device
 */
export type PreMadeModelInfo = {
    name: string;
    model_id: string;
    training_state: TrainingState;
    training_percentage: number;
    gestures: Array<GestureInfo>;
    sample_period_s: number;
    num_rest_recordings: number;
    sample_frequency_hz: number;
    num_channels: number;
    samples_per_inference: number;
};

