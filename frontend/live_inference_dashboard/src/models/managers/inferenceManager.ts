import { getRecoil, setRecoil } from "recoil-nexus";
import { RecordingStreamingService } from "../../clients/inference";

import { authAtom, inferenceMessageAtom } from "../atoms/apiAtoms";
import { inferenceConnectionAtom } from "../atoms/UIAtoms";



var global_ws : WebSocket | null = null;

export default {

    _ws : null,

    save_recording : async (gesture_id: string, session_id: string)=> {
        await RecordingStreamingService.getSaveRecordingSaveRecordingSessionIdGestureIdGet(session_id, gesture_id);
    },

    save_rest_recording : async (model_id: string, session_id: string)=> {
        await RecordingStreamingService.getSaveRestRecordingSaveRestRecordingSessionIdModelIdGet(session_id, model_id);
    },

    connect: async (modelID: string, streamID: string, modelName: string)=> {
        if (global_ws != null){
            global_ws.close();
        }
        const authValue = getRecoil(authAtom);
        const ws = new WebSocket(`ws://localhost:8006/inference/${streamID}/${modelID}/${authValue.email}/${authValue.password}`);
        ws.onopen =() => {
            console.log('connected')
            setRecoil(inferenceConnectionAtom, {
                connected: true,
                streamID: streamID,
                modelName: modelName,
                modelID: modelID,
            });
            setRecoil(inferenceMessageAtom, null);
        };

        ws.onmessage = (event) => {
            const json = JSON.parse(event.data);
            if (json['inference']!== "Rest"){
                console.log(json)
            }
            // console.log(json)
            if(getRecoil(inferenceMessageAtom) !== json['inference']){
                setRecoil(inferenceMessageAtom, json['inference'])
            };
        };

        ws.onclose = () => {
            console.log('closed')
            setRecoil(inferenceConnectionAtom, {
                connected: false,
                streamID:  null,
                modelName: null,
                modelID: null,
            });
            setRecoil(inferenceMessageAtom, null);
        };

        global_ws = ws;
    },

    close : () => {
        console.log('close')
        if (global_ws === null){
            return;
        }
        global_ws.close();
    }
}
