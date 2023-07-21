import './App.css';
import { css } from 'aphrodite';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import {
  useRecoilState,
  useRecoilValue,
  useSetRecoilState,
} from 'recoil';
import { connectedDeviceAtom, downloadStateAtom, readingsAtom, recordingStateAtom } from './models/atoms';
import { getRecoil, setRecoil } from 'recoil-nexus';
import { DownloadState, MindFeedBluetoothDeviceManager, RecordingState } from './utils/BluetoothManager'


const device_manager = new MindFeedBluetoothDeviceManager(
  (device: BluetoothDevice) => {
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

device_manager.set_on_download_state_change(
  (state) => {
    setRecoil(downloadStateAtom, state);
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
        console.log('Clicked Start Record')
        await device_manager.request_start_recording();
      }
    }>StartRecording</button>
    <button onClick={
      async () => {
        console.log('Clicked Start Record')
        await device_manager.start_recording_download((success, data) => {
          console.log(data)
          let blob = new Blob([data]);

          let formData = new FormData();
          formData.append('recording', blob, 'data.bin')
          console.log(formData)
          var obj = {
            link: 'http://localhost:8000' + '/token',
            object: {
              method: 'POST',
              headers: {
                "Content-Type": "application/x-www-form-urlencoded"
              },
              body: 'username=' + 'test' + '&password=' + 'test'
            }
          }
          fetch(obj.link, obj.object).then(async response => {
            const tokenResponse = (await response.json());
            const token = tokenResponse?.access_token;
            const obj = {
              link: 'http://localhost:8001/recording',
              object: {
                method: 'POST',
                headers: {
                  'Authorization': 'Bearer ' + token,
                },
                body: formData
              }
            };
            fetch(obj.link, obj.object);
            // TODO add bad response
          })
          console.log('Download Complete');
          console.log(success);
          // TODO compute the hash of the received bytes
        });
      }
    }>StartDownload</button>
  </>

  // Download Button
  // Login Button
  // Upload Button

}

function App() {
  const connectedDeviceAtomState = useRecoilValue(connectedDeviceAtom);
  const readingsAtomVal = useRecoilValue(readingsAtom);
  const recordingStateAtomVal = useRecoilValue(recordingStateAtom);
  const downloadStateAtomVal = useRecoilValue(downloadStateAtom);

  return <>
    <h1>Current Reading: {readingsAtomVal.slice(-1)}</h1>
    <h1>Connected Device Name: {connectedDeviceAtomState == null ? '' : connectedDeviceAtomState.device_name}</h1>
    <h1>Recording State: {RecordingState[recordingStateAtomVal]}</h1>
    <h1>Download State: {DownloadState[downloadStateAtomVal]}</h1>
    <ConnectToDeviceButton></ConnectToDeviceButton>
  </>
}


export default App;
