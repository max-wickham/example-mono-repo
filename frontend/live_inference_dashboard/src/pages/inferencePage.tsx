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
import { gesturesAtom, inferenceMessageAtom, preMadeModelsAtom } from "../models/atoms/apiAtoms";
import inferenceManager from "../models/managers/inferenceManager";
import { inferenceConnectionAtom, lastRefreshTimeAtom, selectedModelIDAtom } from "../models/atoms/UIAtoms";
import modelsManager from "../models/managers/modelsManager";
import { bluetoothStateAtom, deviceStateAtom } from "../models/atoms/bluetoothAtoms";
import { GestureInfo, PreMadeModelInfo, TrainingState } from "../clients/model";
import { setRecoil } from "recoil-nexus";
import React from 'react';
import recordingsManager from "../models/managers/recordingsManager";
import authManager from "../models/managers/authManager";

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

const recordingModelAtom = atom<boolean>({
    key: 'recordingModelAtom',
    default: false,
})

const DeviceBar = memo(function () {
    const bluetoothStateValue = useRecoilValue(bluetoothStateAtom);
    const deviceStateValue = useRecoilValue(deviceStateAtom);

    const height = 50;
    const padding = 5;

    const barContent = bluetoothStateValue == null || !bluetoothStateValue.connected ?
        <>
            <Button>Connect to device</Button>
        </>
        :
        <Row>
            <Col  xs='auto'>
                <Row className="justify-content-begin">
                    <Col xs="auto"><CardText style={{ marginRight: 30, width: 400 }}><h4>Device ID: 124325413</h4></CardText></Col>
                    <Col xs="auto"><Alert color="success" className={css(styles.small_alert)}>Wifi Connected</Alert></Col>
                    <Col xs="auto"><Alert color="success" className={css(styles.small_alert)}>Streaming</Alert></Col>
                </Row>
            </Col>

            <Col>
                <Row className="justify-content-end">
                    <Col xs="auto"><Button color="primary" className={css(styles.button)}>Setup Wifi</Button></Col>
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
    const setRecordingModel = useSetRecoilState(recordingModelAtom);
    const deviceState = useRecoilValue(deviceStateAtom);
    const lastRefreshTime = useRecoilValue(lastRefreshTimeAtom);
    console.log("rerendering");
    console.log(preMadeModelsValue);

    function requiresRecordings(model: PreMadeModelInfo) {
        var result = model.gestures.length > 0;
        for (const gesture of model.gestures) {
            result = result && gesture.recording_complete_percentage === 100;
        }
        return !result;
    }

    return <Card className={css(styles.card)}>
        <CardHeader><h3 className={css(styles.header)}>Models</h3></CardHeader>
        <CardBody style={{ minHeight: 200, maxHeight: 200, overflowY: 'auto' }}>
            {preMadeModelsValue == null ? <></> :
                preMadeModelsValue.models.map((model) => {
                    // console.log(requiresRecordings(model));
                    return <>
                        <Row>
                            <Col xs='auto'>
                                <Row className="justify-content-begin">
                                    <Col xs="auto"><CardText style={{ marginRight: 30, width: 400 }}><h4>{model.name}</h4></CardText></Col>
                                    {model.training_state === TrainingState.COMPLETE ? <Col xs="auto">
                                        <Alert color="success" className={css(styles.alert)}>Deployable</Alert>
                                    </Col> : <></>}
                                    {model.training_state === TrainingState.IN_PROGRESS ?
                                        <Col xs="auto">
                                            <Alert color="warning" className={css(styles.alert)}>Training</Alert>
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
                                            <Button color="danger" className={css(styles.button)} outline onClick={() => { setRecordingModel(true); setRecoil(selectedModelIDAtom, model.model_id) }}>Collect Recordings</Button> : <></>}
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
                                                <Button className={css(styles.button)} outline onClick={() => { }}>Manage Recording</Button> : <></>}
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
})

const RecordingCard = memo(function () {

    const [isRecording, setIsRecording] = useState(false);
    const [squareCounter, setSquareCount] = useState(0);
    const modelsValue = useRecoilValue(preMadeModelsAtom);
    const selectedModelID = useRecoilValue(selectedModelIDAtom);
    const [selectedGesture, setSelectedGesture] = useState<GestureInfo | null>(null);


    const selectedModel = modelsValue?.models.filter((model) => model.model_id === selectedModelID)[0];
    if (selectedModel === undefined) {
        return <></>;
    }
    // console.log(squareCounter);
    // console.log(selectedGestureID);

    function runSquareCounter() {
        setTimeout(() => { console.log('1'); setIsRecording(true); setSquareCount(1); }, 10);
        setTimeout(() => { console.log('2'); setSquareCount(4) }, 1500);
        setTimeout(() => {
            setSquareCount(0);
            setIsRecording(false);
            if (selectedGesture !== null) {
                inferenceManager.save_recording(selectedGesture?.gesture_id, "12");
            }
            // TODO save the gesture
            // Also reload the models with a short delay after
            setTimeout(() => { modelsManager.getPreMadeModels() }, 2100);
        }, 2000);
    }

    // if (selectedGestureID === null && squareCounter !== 0) {
    //     setSquareCount(0);

    // }


    if (isRecording && selectedGesture !== null) {
        return <Card className={css(styles.card)}>
            <CardHeader><h3>Gesture: {selectedGesture.name}</h3></CardHeader>
            <CardBody style={{ maxHeight: 700, overflowY: 'auto' }}>
                <CardText>Do gesture while green light shows</CardText>
                <div className="col d-flex justify-content-center"><div style={{
                    width: 200,
                    height: 200,
                    backgroundColor: squareCounter < 2 ? 'gray' : 'green',
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
                <Row><Button color="primary" outline onClick={() => runSquareCounter()} style={{ marginBottom: 215 }}>Start</Button></Row>
            </CardBody>
        </Card >
    }

    return <Card className={css(styles.card)}>
        <CardHeader><h3>Gesture: {selectedModel.name}</h3></CardHeader>
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
})

export default function () {
    const [inferenceModalOpen, setInferenceModalOpen] = useRecoilState(inferenceModalAtom);
    const [recordingModelOpen, setRecordingModelOpen] = useRecoilState(recordingModelAtom);

    useEffect(() => {
        // Define a function to make the API call
        const fetchData = async () => {
            await modelsManager.getPreMadeModels();
            await recordingsManager.getGestures();
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
            <img src="/logo.png" style={{ marginLeft: 50, marginTop: 30 }}></img>
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
