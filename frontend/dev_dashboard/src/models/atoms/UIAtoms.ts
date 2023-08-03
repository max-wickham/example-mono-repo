import { atom } from "recoil";

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
