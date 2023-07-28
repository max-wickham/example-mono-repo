import { atom } from "recoil";




export const loginPageUIAtom = atom<{
    incorrectPassword : boolean
}>({
    key: 'loginPageUIAtom',
    default: {
        incorrectPassword: false,
    }
})
