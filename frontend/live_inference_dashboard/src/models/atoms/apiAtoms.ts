/*
Atoms relating to state taken via the backend api
*/

import { atom } from "recoil";
import { PreMadeModelInfo, PreMadeModels } from "../../clients/model";
import { Gestures } from "../../clients/recording";


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
    key: '',
    default: null
});
