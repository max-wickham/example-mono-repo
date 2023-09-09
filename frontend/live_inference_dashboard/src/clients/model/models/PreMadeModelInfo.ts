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
    gestures: Array<GestureInfo>;
};

