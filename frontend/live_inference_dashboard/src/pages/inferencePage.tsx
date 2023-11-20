import { memo, useEffect, useState } from "react";
import { StyleSheet, css } from 'aphrodite';

import {
    Button,
    Row,
    Col,
    Form,
    FormGroup,
    Input,
    Container,
    ButtonGroup,
    Badge,
    Alert,
    Modal, ModalHeader, ModalBody, ModalFooter,
    Card,
    CardText,
    CardHeader,
    CardBody,
    CardTitle
} from "reactstrap";
import { atom, useRecoilState, useRecoilValue, useSetRecoilState } from "recoil";
import { activeAtom, channelCountAtom, channelFrequencyAtom, gesturesAtom, inferenceMessageAtom, preMadeModelsAtom } from "../models/atoms/apiAtoms";
import inferenceManager from "../models/managers/inferenceManager";
import { inferenceConnectionAtom, lastRefreshTimeAtom, selectedModelIDAtom } from "../models/atoms/UIAtoms";
import modelsManager from "../models/managers/modelsManager";
import { bluetoothStateAtom, deviceStateAtom } from "../models/atoms/bluetoothAtoms";
import { GestureInfo, PreMadeModelInfo, TrainingState } from "../clients/model";
import { getRecoil, setRecoil } from "recoil-nexus";
import React from 'react';
import recordingsManager from "../models/managers/recordingsManager";
import authManager from "../models/managers/authManager";

const STREAM_ID = "201326592";
const rowElementHeight = 60;

const styles = StyleSheet.create({
    models_container: {
        border: '5px solid',
        margin: 'auto',
        width: '400px',
        padding: '10px',
        marginTop: 50,
        borderRadius: 10,
    },

    connected_div: {
        backgroundColor: 'green'
    },

    button: {
        height: rowElementHeight,
        width: 150,
    },

    alert: {
        height: rowElementHeight,
        width: 450,
        minWidth: 300
    },

    small_alert: {
        height: rowElementHeight,
        width: 210,
        minWidth: 210
    },

    card: {
        backgroundColor: '#252b37 !important',
        color: '#6d727d',
        border: '0px solid #ddd !important'
    },

    background: {
        backgroundImage: 'linear-gradient(#58566b, #2e3442)',
        width: '100vw',
        height: '100vh',
    },

    header: {
        color: 'white',
        paddingTop: 10,
    }


});

const inferenceModalAtom = atom<boolean>({
    key: 'inferenceModalAtom',
    default: false,
});

const recordingModalAtom = atom<boolean>({
    key: 'recordingModelAtom',
    default: false,
});

const restRecordingModalAtom = atom<boolean>({
    key: 'restRecordingModelAtom',
    default: false,
});


const isRecordingAtom = atom<boolean>({
    key: 'isRecordingAtom',
    default: false,
});

function takeRestRecordings() {
    const selectedModelID = getRecoil(selectedModelIDAtom);
    const modelsValue = getRecoil(preMadeModelsAtom);
    const selectedModel = modelsValue?.models.filter((model) => model.model_id === selectedModelID)[0];
    if (selectedModel === undefined) {
        return;
    }
    // Also reload the models with a short delay after
    if (getRecoil(restRecordingModalAtom) && selectedModel !== null && selectedModel !== undefined) {
        console.log(selectedModel.sample_period_s * 1000);
        inferenceManager.save_rest_recording(selectedModel.model_id, STREAM_ID);
        setTimeout(takeRestRecordings, selectedModel.sample_period_s * 1000);
    }
}

const DeviceBar = memo(function () {
    const bluetoothStateValue = useRecoilValue(bluetoothStateAtom);
    const deviceStateValue = useRecoilValue(deviceStateAtom);
    const active = useRecoilValue(activeAtom);
    const height = 50;
    const padding = 5;

    useEffect(() => {
        // Define a function to make the API call
        const fetchData = async () => {
            await inferenceManager.stream_active(STREAM_ID);
            await inferenceManager.stream_count(STREAM_ID);
            await inferenceManager.stream_frequency(STREAM_ID);
        };
        fetchData();
        // console.log('set')
        const intervalId = setInterval(fetchData, 2000);
        return () => clearInterval(intervalId);
    }, []);

    const barContent = bluetoothStateValue == null || !bluetoothStateValue.connected ?
        <>
            <Button>Connect to device</Button>
        </>
        :
        <Row>
            <Col xs='auto'>
                <Row className="justify-content-begin">
                    <Col xs="auto"><CardText style={{ marginRight: 30, width: 400 }}><h4>Device ID: 124325</h4></CardText></Col>
                    <Col xs="auto"><Alert color="success" className={css(styles.small_alert)}>Wifi Connected</Alert></Col>
                    {
                        active ?
                            <Col xs="auto"><Alert color="success" className={css(styles.small_alert)}>Streaming</Alert></Col> :
                            <Col xs="auto"><Alert color="danger" className={css(styles.small_alert)}>Disconnected</Alert></Col>
                    }

                </Row>
            </Col>

            <Col>
                <Row className="justify-content-end">
                    <Col xs="auto"><Button color="primary" className={css(styles.button)}>Setup Wifi connection</Button></Col>
                    {/* <Col xs="auto"></Col> */}
                </Row>
            </Col>
        </Row>


    return <Card className={css(styles.card)}>
        <CardHeader><h3 className={css(styles.header)}>Device Information</h3></CardHeader>
        <CardBody>
            {barContent}
        </CardBody>
    </Card>

    return <Container style={{
        height: height + padding * 2,
        padding: padding,
        border: '5px solid',
        // width: 'auto',
        // display: 'flex',
        // float: 'left',
        // alignItems: 'left',
        // justifyContent: 'flex-start',
        width: '100vh'
    }}>{barContent}</Container>
});

const ModelsCard = function () {
    const preMadeModelsValue = useRecoilValue(preMadeModelsAtom);
    const setInferenceModal = useSetRecoilState(inferenceModalAtom);
    const setRecordingModal = useSetRecoilState(recordingModalAtom);
    const setRestRecordingModal = useSetRecoilState(restRecordingModalAtom);
    const deviceState = useRecoilValue(deviceStateAtom);
    const lastRefreshTime = useRecoilValue(lastRefreshTimeAtom);
    const numChannels = useRecoilValue(channelCountAtom);
    const sessionFrequency = useRecoilValue(channelFrequencyAtom);

    function requiresRecordings(model: PreMadeModelInfo) {
        var result = model.gestures.length > 0;
        for (const gesture of model.gestures) {
            result = result && gesture.recording_complete_percentage === 100;
        }
        return !result;
    }

    console.log(numChannels);
    console.log(sessionFrequency);
    return <Card className={css(styles.card)}>
        <CardHeader><h3 className={css(styles.header)}>Models</h3></CardHeader>
        <CardBody style={{ minHeight: 200, maxHeight: 200, overflowY: 'auto' }}>
            {preMadeModelsValue == null ? <></> :
                preMadeModelsValue.models
                    .filter((model) => model.num_channels === numChannels)
                    .filter((model) => model.sample_frequency_hz === sessionFrequency)
                    .map((model) => {
                    // console.log(requiresRecordings(model));
                    return <>
                        <Row>
                            <Col xs='auto'>
                                <Row className="justify-content-begin">
                                    <Col xs="auto"><CardText style={{ marginRight: 30, width: 180 }}><h4>{model.name}</h4></CardText></Col>
                                    <Col xs="auto"><CardText style={{ marginRight: 30, width: 170 }}><h4>Rest Data: {model.num_rest_recordings}</h4></CardText></Col>
                                    {model.training_state === TrainingState.COMPLETE ? <Col xs="auto">
                                        <Alert color="success" className={css(styles.alert)}>Deployable</Alert>
                                    </Col> : <></>}
                                    {model.training_state === TrainingState.IN_PROGRESS ?
                                        <Col xs="auto">
                                            <Alert color="warning" className={css(styles.alert)}>Training {model.training_percentage}%</Alert>
                                        </Col> : <></>}
                                    {requiresRecordings(model) ?
                                        <Col xs="auto">
                                            <Alert color="danger" className={css(styles.alert)}>Requires Recording</Alert>
                                        </Col> : <></>}
                                </Row>
                            </Col>

                            <Col>
                                <Row className="justify-content-end">
                                    <Col xs="auto">
                                        {model.training_state === TrainingState.COMPLETE ? <Button outline color="success" className={css(styles.button)} onClick={
                                            () => {
                                                setInferenceModal(true);
                                                if (deviceState != null && deviceState.stream_id != null) {
                                                    console.log('starting inference')
                                                    inferenceManager.connect(model.model_id, deviceState.stream_id, model.name);
                                                }
                                            }}>Run Inference</Button> : <></>}
                                    </Col>
                                    <Col xs="auto">
                                        {(!requiresRecordings(model)) && model.training_state !== TrainingState.IN_PROGRESS ?
                                            <Button color="warning" className={css(styles.button)} outline
                                                onClick={async () => {
                                                    await modelsManager.trainModel(model.model_id)
                                                }}
                                            >Train</Button> : <></>}
                                    </Col>
                                    <Col xs="auto">
                                        {true ?
                                            <Button color="danger" className={css(styles.button)} outline onClick={() => { setRecordingModal(true); setRecoil(selectedModelIDAtom, model.model_id) }}>Collect Recordings</Button> : <></>}
                                    </Col>
                                    <Col xs="auto">
                                        {true ?
                                            <Button color="danger" className={css(styles.button)} outline onClick={() => {
                                                setRestRecordingModal(true); setRecoil(selectedModelIDAtom, model.model_id);
                                                setTimeout(takeRestRecordings, model.sample_period_s * 1000);
                                            }}>Collect Rest Data</Button> : <></>}
                                    </Col>
                                    <Col xs="auto">
                                        {true ?
                                            <Button color="danger" className={css(styles.button)} outline onClick={() => recordingsManager.clearRestData(model.model_id)}>Clear Rest Data</Button> : <></>}
                                    </Col>
                                </Row>
                            </Col>
                        </Row>
                    </>
                })
            }
        </CardBody>
    </Card>
}

const GesturesCard = function () {

    const gesturesValue = useRecoilValue(gesturesAtom);

    if (gesturesValue == null) {
        return <></>
    }
    return <Card className={css(styles.card)}>
        <CardHeader><h3 className={css(styles.header)}>Gestures</h3></CardHeader>
        <CardBody style={{ maxHeight: 700, overflowY: 'auto' }}>

            {
                (gesturesValue == null) ? <></> :
                    Object.entries(gesturesValue?.gestures).map(([_, gesture]) => {
                        return <>
                            <Row>
                                <Col>
                                    <Row className="justify-content-begin">
                                        <Col xs="auto"><CardText style={{ marginRight: 30, width: 400 }}><h4>{gesture.name}</h4></CardText></Col>
                                        <Col xs="auto"><Alert>Num Recordings: {gesture.num_recordings}</Alert></Col>
                                    </Row>
                                </Col>

                                <Col>
                                    <Row className="justify-content-end">
                                        <Col xs="auto">
                                            {true ?
                                                <Button className={css(styles.button)} outline onClick={async () => {
                                                    await recordingsManager.clearGesture(gesture.gesture_id);
                                                    await modelsManager.getGestures();
                                                }}>Delete Recording</Button> : <></>}
                                        </Col>
                                    </Row>
                                </Col>
                            </Row>
                        </>
                    })
            }
        </CardBody>
    </Card>
}

const InferenceCard = memo(function () {
    const inferenceConnection = useRecoilValue(inferenceConnectionAtom);
    const inferenceMessage = useRecoilValue(inferenceMessageAtom);
    // console.log(inferenceMessage);
    return <Card className={css(styles.card)}>
        <CardHeader className="{css(styles.card)}">{inferenceConnection.modelName}</CardHeader>
        <CardBody style={styles.card}>
            <Alert color="dark">{inferenceMessage}</Alert>
        </CardBody>
    </Card>
});

const RecordingCard = memo(function () {

    const [isRecording, setIsRecording] = useRecoilState(isRecordingAtom);
    const [squareGreen, setSquareGreen] = useState(false);
    const modelsValue = useRecoilValue(preMadeModelsAtom);
    const selectedModelID = useRecoilValue(selectedModelIDAtom);
    const [selectedGesture, setSelectedGesture] = useState<GestureInfo | null>(null);

    const selectedModel = modelsValue?.models.filter((model) => model.model_id === selectedModelID)[0];
    if (selectedModel === undefined) {
        return <></>;
    }

    const greyTime = 1000;

    function continuousSamples() {                    // setIsRecording(false);
        // Also reload the models with a short delay after
        if (getRecoil(isRecordingAtom) && selectedGesture !== null && selectedModel !== undefined) {
            console.log("sample");
            inferenceManager.save_recording(selectedGesture.gesture_id, STREAM_ID);
            if (selectedGesture.continuous) {
                console.log('continous')
                setTimeout(continuousSamples, selectedModel.sample_period_s * 1000);
            } else {
                console.log('not continous')
                setSquareGreen(false);
                setIsRecording(false);
            }
        }
    }



    function runSquareCounter() {
        setIsRecording(true);
        console.log("hello");

        setTimeout(() => { setIsRecording(true); console.log(isRecording); setSquareGreen(false); console.log(isRecording); }, 10);


        if (selectedModel !== undefined && selectedGesture !== null) {
            setTimeout(() => { console.log('heello'); setSquareGreen(true) }, greyTime);
            // setTimeout(() => { console.log('heello'); setSquareGreen(false) }, greyTime + 1000);
            // if (selectedGesture.continuous) {
            setTimeout(continuousSamples, greyTime + selectedModel.sample_period_s * 1000)
            // } else {
            //     setTimeout(() => {
            //         if (isRecording && selectedGesture !== null) {
            //             inferenceManager.save_recording(selectedGesture?.gesture_id, STREAM_ID);
            //         }
            //         setSquareGreen(false);
            //         setTimeout(() => { modelsManager.getPreMadeModels() }, selectedModel === undefined ? greyTime : greyTime + selectedModel.sample_period_s + 100);
            //     }, greyTime + selectedModel.sample_period_s);
            // }
        }
    }

    if (isRecording && selectedGesture !== null) {
        console.log(isRecording);
        return <Card className={css(styles.card)}>
            <CardHeader>
                <h3>Gesture: {selectedGesture.name}</h3>
                {selectedGesture.continuous ?
                    <Col><Row className="justify-content-end">
                        <Button
                            color="danger"
                            onClick={() => { setIsRecording(false); setSquareGreen(false); modelsManager.getPreMadeModels(); }}
                            style={{ width: 100, marginRight: 10 }}
                        >Exit</Button></Row></Col> : <></>}
            </CardHeader>
            <CardBody style={{ maxHeight: 700, overflowY: 'auto' }}>
                <CardText>Do gesture while green light shows</CardText>
                <div className="col d-flex justify-content-center"><div style={{
                    width: 200,
                    height: 200,
                    backgroundColor: squareGreen ? 'green' : 'gray',
                    marginBottom: 30,
                    marginTop: 20,
                }}
                ></div></div>
            </CardBody>
        </Card>
    }

    if (selectedGesture !== null) {
        return <Card className={css(styles.card)}>
            <CardHeader>
                <Row>
                    <Col><Row className="justify-content-begin"> <h3>Gesture: {selectedGesture.name}</h3></Row></Col>
                    <Col><Row className="justify-content-end">
                        <Button
                            color="danger"
                            onClick={() => setSelectedGesture(null)}
                            style={{ width: 100, marginRight: 10 }}
                        >Exit</Button></Row></Col>
                </Row>
            </CardHeader>
            {/* <Row className="justify-content-end"></Row> */}
            <CardBody style={{ maxHeight: 700, overflowY: 'auto' }}>
                <CardText>Do gesture while green light shows</CardText>
                <Row><Button color="primary" outline onClick={() => { setIsRecording(true); runSquareCounter() }} style={{ marginBottom: 215 }}>Start</Button></Row>
            </CardBody>
        </Card >
    }

    return <Card className={css(styles.card)}>
        <CardHeader><h3>Model: {selectedModel.name}</h3></CardHeader>
        <CardBody style={{ maxHeight: 700, overflowY: 'auto', maxWidth: 900 }}>
            {selectedModel === null ? <></> :
                selectedModel.gestures.map((gesture) => {
                    return <Row>
                        <Col><Alert color={gesture.recording_complete_percentage === 100 ? "success" : "dark"} style={{ width: 300, height: rowElementHeight }}>Gesture Name: {gesture.name}</Alert></Col>
                        <Col><Alert color={gesture.recording_complete_percentage === 100 ? "success" : "dark"} style={{ width: 300, height: rowElementHeight }}>  Recordings: {gesture.num_recordings}</Alert></Col>
                        <Col><Button color="success" outline onClick={() => setSelectedGesture(gesture)} style={{ height: rowElementHeight }}>Record</Button></Col>
                    </Row>

                })
            }
        </CardBody>
    </Card>
});

const RestRecordingCard = memo(function () {

    const selectedModelID = useRecoilValue(selectedModelIDAtom);
    const modelsValue = useRecoilValue(preMadeModelsAtom);

    const selectedModel = modelsValue?.models.filter((model) => model.model_id === selectedModelID)[0];
    if (selectedModel === undefined) {
        return <></>;
    }

    //  Currently recording rest data, dont do any gestures
    //

    return <Card className={css(styles.card)}>
        <Row>
            <Col><Row className="justify-content-begin"> <h3>Model: {selectedModel.name}</h3></Row></Col>
            <Col><Row className="justify-content-end">
                <Button
                    color="danger"
                    onClick={() => { setRecoil(restRecordingModalAtom, false); }}
                    style={{ width: 100, marginRight: 10 }}
                >Exit</Button></Row></Col>
        </Row>
        <CardBody>
            <Alert color="danger">Recording Rest Data</Alert>
        </CardBody>
    </Card>
});

export default function () {
    const [inferenceModalOpen, setInferenceModalOpen] = useRecoilState(inferenceModalAtom);
    const [recordingModelOpen, setRecordingModelOpen] = useRecoilState(recordingModalAtom);
    const [restRecordingModalOpen, setRestRecordingModelOpen] = useRecoilState(restRecordingModalAtom);

    useEffect(() => {
        // Define a function to make the API call
        const fetchData = async () => {
            await modelsManager.getPreMadeModels();
            await modelsManager.getGestures();
        };
        fetchData();
        // console.log('set')
        const intervalId = setInterval(fetchData, 2000);
        return () => clearInterval(intervalId);
    }, []);

    function toggleInferenceModal() {
        if (inferenceModalOpen) {
            inferenceManager.close();
        }
        setInferenceModalOpen(!inferenceModalOpen);
    }

    const separator = <div style={{
        padding: 0,
        marginTop: 10,
        // backgroundColor: '#f0f0f0',
        border: '1px solid #ddd'
    }}></div>

    const padding = 40;
    const sideBarWidth = 500;
    return (<div className={css(styles.background)}>
        <div style={{
            width: sideBarWidth,
            // backgroundColor: '#58566b',
            height: '100vh',
            position: 'absolute'
        }}>
            <img src="/logo.png" style={{ marginLeft: 50, marginTop: 30, width: 100, height: 80 }}></img>
            {/* <h2 style={{padding: 20, color: 'white'}}>MindFeed Dashboard</h2> */}
            {/* {separator} */}

            <div style={{ marginTop: 30, marginLeft: 50, fontSize: 30, color: '#dad9e7' }}>Dashboard</div>
            <div style={{ marginTop: 30, marginLeft: 50, fontSize: 30, color: '#7d7e92' }}>Account</div>
            <Button color='danger' style={{ position: 'absolute', bottom: 30, left: 50 }}
                onClick={authManager.logout}
            >Logout</Button>
        </div>
        <div style={{
            // backgroundColor: '#58566b',
            width: '100%',
            marginLeft: sideBarWidth,
            height: '100vh',
            position: 'absolute',
            padding: padding,
            paddingRight: padding + sideBarWidth,
        }}>
            {/* Inference Modal */}
            <Modal isOpen={inferenceModalOpen} toggle={toggleInferenceModal} className="modal-dialog-centered">
                <ModalHeader toggle={toggleInferenceModal} className={css(styles.card)}>Live Inference</ModalHeader>
                <ModalBody className={css(styles.card)}>
                    <InferenceCard></InferenceCard>
                </ModalBody>
                <ModalFooter className={css(styles.card)}>
                </ModalFooter>
            </Modal>
            {/* Recording Modal */}
            <Modal isOpen={recordingModelOpen} toggle={() => setRecordingModelOpen(!recordingModelOpen)} className={"modal-dialog-centered modal-lg"}>
                <ModalHeader toggle={() => setRecordingModelOpen(!recordingModelOpen)} className={css(styles.card)}>Gesture Recording</ModalHeader>
                <ModalBody className={css(styles.card)}>
                    <RecordingCard></RecordingCard>
                </ModalBody>
                <ModalFooter className={css(styles.card)}>
                </ModalFooter>
            </Modal>
            <Modal isOpen={restRecordingModalOpen} toggle={() => setRestRecordingModelOpen(!restRecordingModalOpen)} className={"modal-dialog-centered modal-lg"}>
                <ModalHeader toggle={() => setRestRecordingModelOpen(!restRecordingModalOpen)} className={css(styles.card)}>Rest Recording</ModalHeader>
                <ModalBody className={css(styles.card)}>
                    <RestRecordingCard></RestRecordingCard>
                </ModalBody>
                <ModalFooter className={css(styles.card)}>
                </ModalFooter>
            </Modal>
            <div style={{ marginBottom: padding, maxHeight: 300 }}>
                <DeviceBar></DeviceBar>
            </div>
            <div style={{ marginBottom: padding, maxHeight: 300 }}>
                <ModelsCard></ModelsCard>
            </div>
            <div style={{ marginBottom: padding, maxHeight: 300 }}>
                <GesturesCard></GesturesCard>
            </div>
        </div>
    </div>
    );
};
