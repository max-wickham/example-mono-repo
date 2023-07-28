/*
Atoms relating to state taken via the backend api
*/

import { atom } from "recoil";


export const authAtom = atom<{
    loggedIn: boolean,
    token: string | null,
}>({
    key : 'authAtom',
    default : {
        loggedIn: false,
        token: null
    }
})
