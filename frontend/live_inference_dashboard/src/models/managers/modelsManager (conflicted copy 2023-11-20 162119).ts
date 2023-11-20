import { setRecoil } from "recoil-nexus";
import { GesturesService, PreMadeModelsService } from "../../clients/model"
import { gesturesAtom, preMadeModelsAtom } from "../atoms/apiAtoms";
import { OpenAPI as OpenAPIModel } from "../../clients/model";
import { ModelsService } from "../../clients/model/services/ModelsService";
import { lastRefreshTimeAtom } from "../atoms/UIAtoms";
// import { lastRefreshTimeAtom } from "../atoms/UIAtoms";



export default {

    getPreMadeModels: async () => {
        const preMadeModels = await PreMadeModelsService.getPreMadeModelsPreMadeModelsGet();
        console.log(preMadeModels);
        setRecoil(lastRefreshTimeAtom, new Date().getTime());
        setRecoil(preMadeModelsAtom, preMadeModels);
    },

    trainModel: async (model_id: string) => {
        console.log('sent')
        await ModelsService.postModelModelModelIdPost(model_id)
    },

    getGestures: async function () {
        try {
            // TODO get the list of gestures and their information
            const response = await GesturesService.getGesturesGesturesGet();
            // Set the gestures in the recoil atom
            setRecoil(gesturesAtom, response);
        } catch {
            console.log('Error getting gestures');
        }
    },

    createGesture: async function (gesture_info: {
        name: string,
        comments: string,
        continuous: boolean,
        sampling_frequency_hz: number,
        num_samples_per_recording: number,
        num_recordings_required: number,
        num_channels: number,
    }) {
        try {
            await GesturesService.postGestureGesturePost(gesture_info);
            await this.getGestures();
        } catch {
            console.log('Error getting gestures');
        }
    },

    createModel: async function (model_info: {
        name: string,
        gestures: string[],
        model_weights: string,
        sample_period_s: number,
        sample_number: number,
        sample_frequency_hz: number,
        has_rest_class: boolean,
        num_channels: number,
    }) {
        try {
            await ModelsService.postPreMadeModelPreMadeModelPost(model_info);
            await this.getPreMadeModels();
        } catch {
            console.log('Error getting gestures');
        }
    },

    deleteModel: async function (model_id: string) {
        await ModelsService.delModelModelModelIdDelete(model_id);
    },

    deleteGesture: async function (gesture_id: string) {
        await GesturesService.delGestureGestureGestureIdDelete(gesture_id);
    },

}
