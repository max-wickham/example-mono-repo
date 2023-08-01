import { memo } from "react";
import { useRecoilValue } from "recoil";
import { gesturesAtom } from "../../models/atoms/apiAtoms";
import recordingsManager from '../../models/managers/recordingsManager';


export default memo(props => {
    const gesturesAtomState = useRecoilValue(gesturesAtom);
    // TODO show a list of gestures each with the recording number and recording percentage

    // Provide a modal that allows for actual recordings to take place

    // Request the current gestures
    recordingsManager.getGestures()
    return <>

    </>;
});
