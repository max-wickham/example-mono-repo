import { memo } from "react";
import { Modal, ModalHeader } from "reactstrap";
import { useRecoilState, useRecoilValue } from "recoil";
import { gesturesAtom } from "../../models/atoms/apiAtoms";
import { createRecordingModalAtom, selectedGestureKeyAtom } from "../../models/atoms/UIAtoms";


export default memo(() => {
    const [createRecordingVal, setCreateRecording] = useRecoilState(createRecordingModalAtom);
    const gestureAtomVal = useRecoilValue(gesturesAtom);
    const selectedGestureKey = useRecoilValue(selectedGestureKeyAtom);

    const gesture = selectedGestureKey == null || gestureAtomVal == null ?
        null : gestureAtomVal.gestures[selectedGestureKey];

    return <>
        <Modal isOpen={createRecordingVal} style={{ width: 600, minWidth: 300 }}>
            <ModalHeader toggle={() => { setCreateRecording(!createRecordingVal) }}>
                Create Gesture Recordings
            </ModalHeader>
            {
                gesture == null ? <></> :
                    <>
                        <p>Name: {gesture.name}</p>
                        <p>Num Recordings: {gesture.num_recordings}</p>
                    </>
            }

        </Modal>
    </>
});
