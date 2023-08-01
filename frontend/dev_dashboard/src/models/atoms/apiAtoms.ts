/*
Atoms relating to state taken via the backend api
*/

import { atom } from "recoil";
import { Gestures } from "../../clients/recording";


export const authAtom = atom<{
    loggedIn: boolean,
    token: string | null,
}>({
    key : 'authAtom',
    default : {
        loggedIn: true,
        token: null
    }
})


export const gesturesAtom = atom<Gestures|null>({
    key: 'gesturesAtom',
    default: null,
})
