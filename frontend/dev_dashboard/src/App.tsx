import './App.css';
import { css } from 'aphrodite';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import {
  useRecoilState,
  useRecoilValue,
  useSetRecoilState,
} from 'recoil';
import { connectedDeviceAtom, readingsAtom, recordingStateAtom } from './models/atoms';
import { getRecoil, setRecoil } from 'recoil-nexus';
import { MindFeedBluetoothDeviceManager } from './utils/BluetoothManager'


const device_manager = new MindFeedBluetoothDeviceManager(
  (device : BluetoothDevice) => {
    setRecoil(connectedDeviceAtom, {
      device_name: device.name == undefined ? 'Na' : device.name,
      connected: device.gatt?.connected == undefined ? false : device.gatt?.connected
    });
  },
  () => {
    setRecoil(connectedDeviceAtom, {
      device_name: 'None',
      connected: false,
    });
  }
);

device_manager.set_on_reading(
  (reading) => {
    setRecoil(readingsAtom, [...getRecoil(readingsAtom), reading])
  }
)

device_manager.set_on_recording_state_change(
  (state) => {
    setRecoil(recordingStateAtom, state);
  }
)


function ConnectToDeviceButton() {

  return <>
    <button onClick={
      async () => {
        await device_manager.connect()
      }
    }>Connect to Device</button>
    <button onClick={
      async () => {
        await device_manager.start_recording_download(() => {});
      }
    }>StartRecording</button>
  </>
}

function App() {
  const connectedDeviceAtomState = useRecoilValue(connectedDeviceAtom);
  const readingsAtomVal = useRecoilValue(readingsAtom);
  const recordingStateAtomVal = useRecoilValue(recordingStateAtom);

  return <>
    <h1>Current Reading: {readingsAtomVal.slice(-1)}</h1>
    <h1>Connected Device Name: {connectedDeviceAtomState == null ? '' : connectedDeviceAtomState.device_name}</h1>
    <h1>Recording State: {recordingStateAtomVal.toString()}</h1>
    <ConnectToDeviceButton></ConnectToDeviceButton>
  </>
}


export default App;
