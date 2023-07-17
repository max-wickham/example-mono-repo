import { atom } from "recoil"
import {RecordingState} from "../utils/BluetoothManager"

export const readingsAtom = atom<number[]>({
    key : 'readingsAtom',
    default : [0]
})

export const connectedDeviceAtom = atom<{
    device_name: string,
    connected: boolean
} | null>({
    key: 'connectedDeviceAtom', // unique ID (with respect to other atoms/selectors)
    default: {
        device_name : 'None',
        connected : false
    }
},
);

export const recordingStateAtom = atom<RecordingState>({
    key: 'recordingStateAtom', // unique ID (with respect to other atoms/selectors)
    default: RecordingState.RSNotRecording
},
);
