import { memo } from "react";
import { StyleSheet, css } from 'aphrodite';
import { useRecoilState } from "recoil";
import GesturesList from "./components/gesturesList";
import { createRecordingModalAtom } from "../models/atoms/UIAtoms";
import CreateRecordingModal from "./components/createRecordingModal";
import { Button } from "reactstrap";

const mainPageStyles = StyleSheet.create({
    grid: {
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: 20,
        padding: 20
    }
})

export default memo(() => {
    const [createRecordingModalVal, setCreateRecordingModal] = useRecoilState(createRecordingModalAtom);
    /*
        Split into to pannels, one for models and one for gestures
    */
    return <>
        {/* Grid */}
        <CreateRecordingModal></CreateRecordingModal>
        <div style={{ position: 'fixed' }}></div>
        <div className={css(mainPageStyles.grid)}>
            <div>
                Left
                <h2>Gestures List</h2>
                {/* gestures container */}
                <div>
                    <GesturesList></GesturesList>
                </div>
            </div>
            <div>
                Right
            </div>
        </div>
    </>
});



const Button1 = () => {

    return <>
        <button>Press Me</button>
    </>

}

const MainPage = () => {

    return <>

        <h1>Header</h1>
        <Button1></Button1>
    </>
}
