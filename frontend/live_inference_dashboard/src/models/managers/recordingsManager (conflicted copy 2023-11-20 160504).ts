import { setRecoil } from "recoil-nexus";
import { GestureInfoService, OpenAPI, RecordingUploadsService } from "../../clients/recording"
import { gesturesAtom } from "../atoms/apiAtoms";


export default {

    clearGesture: async function(gestureID: string)  {
        console.log("deleteing gestures");
        await GestureInfoService.deleteGestureRecordingsGesutureRecordingsGestureIdDelete(gestureID);
    },

    clearRestData: async function (modelID: string) {
        console.log("deleteing rest data");
        await GestureInfoService.deleteRestRecordingsRestRecordingsModelIdDelete(modelID);
    },

    download_recordings: async function (gesture_id: string) {
        try {
            const request = await fetch(OpenAPI.BASE + '/recording_files/' + gesture_id, {
                headers: new Headers({
                    'Authorization': 'Bearer ' + OpenAPI.TOKEN,
                    'Content-Type': 'application/x-www-form-urlencoded'
                }),
                method: 'GET'
            });
            const response = await request.blob();
            return response;
        } catch {

        }
    }

}
