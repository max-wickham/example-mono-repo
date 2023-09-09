// import './App.css';
// import "bootstrap/dist/css/bootstrap.min.css";
// import "bootstrap-icons/font/bootstrap-icons.css";
// import { BrowserRouter as Router, Route, Link, BrowserRouter, Routes } from "react-router-dom";
// import styled from "styled-components";
// import { StyleSheet, css } from 'aphrodite';
// import {
//   useRecoilState,
//   useRecoilValue,
//   useSetRecoilState,
// } from 'recoil';
// import { connectedDeviceAtom, downloadStateAtom, readingsAtom, recordingStateAtom } from './models/atoms/bluetoothAtoms';
// import { getRecoil, setRecoil } from 'recoil-nexus';
// import { DownloadState, MindFeedBluetoothDeviceManager, RecordingState } from './utils/BluetoothManager'
// import { authAtom } from './models/atoms/apiAtoms';
// import { LoginPage } from './pages/loginPage';
// import { Button } from 'reactstrap';
// import authManager from './models/managers/authManager';
// import MainPage from './pages/mainPage';

import { Button } from "reactstrap";
import InferencePage from "./pages/inferencePage";
import { BluetoothController } from "./utils/BlutoothController3";
import 'bootstrap/dist/css/bootstrap.css';
import { useRecoilValue } from "recoil";
import { authAtom } from "./models/atoms/apiAtoms";
import { LoginPage } from "./pages/loginPage";
import modelsManager from "./models/managers/modelsManager";

const bluetoothController = new BluetoothController(
  (device)=> {}, () => {}
);

bluetoothController.add_callback("/test_response", async (message) => {
  console.log("message received");
  console.log(message);
})

function App () {
  const authValue = useRecoilValue(authAtom);

  return authValue.loggedIn? <InferencePage></InferencePage> : <LoginPage></LoginPage>;
}

export default App;
