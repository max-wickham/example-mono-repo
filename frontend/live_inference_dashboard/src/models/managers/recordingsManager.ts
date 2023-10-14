import { setRecoil } from "recoil-nexus";
import { GestureInfoService, RecordingUploadsService } from "../../clients/recording"
import { gesturesAtom } from "../atoms/apiAtoms";


export default {

    getGestures: async function () {
        try {
            // TODO get the list of gestures and their information
            const response = await GestureInfoService.getGesturesGesturesGet();
            // Set the gestures in the recoil atom
            setRecoil(gesturesAtom, response);
        } catch {
            console.log('Error getting gestures');
        }
    },

    clearGesture: async function(gestureID: string)  {
        console.log("deleteing gestures");
        await GestureInfoService.deleteGestureRecordingsGesutureRecordingsGestureIdDelete(gestureID);
    }

}
