/*
Atoms relating to state taken via the backend api
*/

import { atom } from "recoil";
import { PreMadeModelInfo, PreMadeModels } from "../../clients/model";
import { Gestures } from "../../clients/model";


export const authAtom = atom<{
    loggedIn: boolean,
    token: string | null,
    email: string | null,
    password: string | null,
}>({
    key : 'authAtom',
    default : {
        loggedIn: false,
        token: null,
        email: null,
        password: null
    }
});


export const gesturesAtom = atom<Gestures|null>({
    key: 'gesturesAtom',
    default: null,
});

export const inferenceMessageAtom = atom<string|null>({
    key : 'inferenceMessage',
    default: null,
});

export const preMadeModelsAtom = atom<PreMadeModels|null>({
    key: 'preMadeModelsAtom',
    default: null
});

export const activeAtom = atom<boolean>({
    key: 'activeAtom',
    default: false
});

export const channelCountAtom = atom<number>({
    key: 'channelCountAtom',
    default: 0,
});

export const channelFrequencyAtom = atom<number>({
    key: 'channelFrequencyAtom',
    default: 0,
});
