import { atom } from "recoil"
import {DownloadState, RecordingState} from "../../utils/BluetoothManager"

/*
Atoms relating to bluetooth state
*/

export const bluetoothStateAtom = atom<{
    device_name: string,
    connected: boolean
} | null>({
    key: 'bluetoothStateAtom', // unique ID (with respect to other atoms/selectors)
    default: {
        device_name : 'MindFeed Device',
        connected : true
    }
},
);

export const deviceStateAtom = atom<{
    wifi_connected : boolean,
    streaming : boolean | null,
    stream_id : string | null,
}| null>({
    key: 'deviceStateAtom',
    default : {
        wifi_connected : true,
        streaming: true,
        stream_id: "201326592",
    },
});
