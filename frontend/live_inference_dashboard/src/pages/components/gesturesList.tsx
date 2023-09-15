import { memo, useState } from "react";
import { useRecoilValue, useSetRecoilState } from "recoil";
import { StyleSheet, css } from 'aphrodite';

import { gesturesAtom } from "../../models/atoms/apiAtoms";
import recordingsManager from '../../models/managers/recordingsManager';
import { Button } from "reactstrap";
import { createRecordingModalAtom, selectedGestureKeyAtom } from "../../models/atoms/UIAtoms";


const gestureListStyles = StyleSheet.create({
    gestureBox: {
        backgroundColor: "#e0e0e0",
        padding: 10,
    },

    gestureListItem: {
        backgroundColor: "#d0d0d0",
        padding: 10,
        marginTop: 10,
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
    },

    gestureListItemBlock: {
        backgroundColor: "#d0d0d0",
        padding: 10,
        marginTop: 10,
    },
})



export default memo(props => {
    const gestureAtomVal = useRecoilValue(gesturesAtom);
    const setCreateRecordingModal = useSetRecoilState(createRecordingModalAtom);
    const setSelectedGestureKey = useSetRecoilState(selectedGestureKeyAtom)
    const gestures = gestureAtomVal == null ? {} : gestureAtomVal.gestures;

    return <>
        <div style={{ height: '500px', overflow: 'auto' }} className={css(gestureListStyles.gestureBox)}>
            {
                Object.keys(gestures).map( gesture_key => {
                    const gesture = gestures[gesture_key];
                    return <div className={css(gestureListStyles.gestureListItem)}>
                        <div style={{marginRight: 10, width: 170}}>
                            Name: {gesture.name}
                        </div>
                        <div style={{marginRight: 10, width: 170}}>
                            Num Recordings: {gesture.num_recordings}
                        </div>
                        <div style={{marginRight: 10, width: 170}}>
                            Percent Complete: {gesture.recording_completion_percentage}
                        </div>
                        <Button onClick={() => {
                            setCreateRecordingModal(true);
                            setSelectedGestureKey(gesture_key);
                        }}>Add Recordings</Button>
                    </div>
                })
            }
        </div>
    </>;
});
