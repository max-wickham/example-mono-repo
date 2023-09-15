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

    sendRecording: async function (recording: ArrayBuffer, gestureID: string) {
        try {
            const blob = new Blob([recording]);
            await RecordingUploadsService.postRecordingRecordingGestureIdPost(
                gestureID,
                {
                    recording: blob
                }
            );
            await this.getGestures();
        } catch {
            console.log('Recording upload failed')
        }
    }

}
