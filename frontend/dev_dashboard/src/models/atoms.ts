import { atom } from "recoil"


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
