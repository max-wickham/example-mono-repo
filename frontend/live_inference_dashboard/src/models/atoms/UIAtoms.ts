import { atom } from "recoil";
import { PreMadeModelInfo } from "../../clients/model";

export const loginPageUIAtom = atom<{
    incorrectPassword : boolean
}>({
    key: 'loginPageUIAtom',
    default: {
        incorrectPassword: false,
    }
});


// Sets whether or not the create recording modal is visible
export const createRecordingModalAtom = atom<boolean>({
    key: 'createRecordingModalAtom',
    default: false,
});

export const selectedGestureKeyAtom = atom<string|null>({
    key: 'selectedGestureKeyAtom',
    default: null,
});

export const inferenceConnectionAtom = atom<{
    connected : boolean,
    modelID: string | null,
    modelName: string | null,
    streamID: string | null,
}>({
    key: 'inferenceConnectionAtom',
    default:{
        connected : false,
        modelID: null,
        modelName: null,
        streamID: null
    }
});

export const lastRefreshTimeAtom = atom<number>({
    key : 'lastRefreshTimeAtom',
    default: 0,
});


export const selectedModelIDAtom = atom<string|null>({
    key : 'selectedModelIDAtom',
    default: null,
})
