import './App.css';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { BrowserRouter as Router, Route, Link, BrowserRouter, Routes } from "react-router-dom";
import styled from "styled-components";
import { StyleSheet, css } from 'aphrodite';
import {
  useRecoilState,
  useRecoilValue,
  useSetRecoilState,
} from 'recoil';
import { connectedDeviceAtom, downloadStateAtom, readingsAtom, recordingStateAtom } from './models/atoms/bluetoothAtoms';
import { getRecoil, setRecoil } from 'recoil-nexus';
import { DownloadState, MindFeedBluetoothDeviceManager, RecordingState } from './utils/BluetoothManager'
import { authAtom } from './models/atoms/apiAtoms';
import { LoginPage } from './pages/loginPage';
import { Button } from 'reactstrap';
import authManager from './models/managers/authManager';
import MainPage from './pages/mainPage';


// const device_manager = new MindFeedBluetoothDeviceManager(
//   (device: BluetoothDevice) => {
//     setRecoil(connectedDeviceAtom, {
//       device_name: device.name == undefined ? 'Na' : device.name,
//       connected: device.gatt?.connected == undefined ? false : device.gatt?.connected
//     });
//   },
//   () => {
//     setRecoil(connectedDeviceAtom, {
//       device_name: 'None',
//       connected: false,
//     });
//   }
// );

// device_manager.set_on_reading(
//   (reading) => {
//     setRecoil(readingsAtom, [...getRecoil(readingsAtom), reading])
//   }
// )

// device_manager.set_on_recording_state_change(
//   (state) => {
//     setRecoil(recordingStateAtom, state);
//   }
// )

// device_manager.set_on_download_state_change(
//   (state) => {
//     setRecoil(downloadStateAtom, state);
//   }
// )


// function ConnectToDeviceButton() {

//   return <>
//     <button onClick={
//       async () => {
//         await device_manager.connect()
//       }
//     }>Connect to Device</button>
//     <button onClick={
//       async () => {
//         console.log('Clicked Start Record')
//         await device_manager.request_start_recording();
//       }
//     }>StartRecording</button>
//     <button onClick={
//       async () => {
//         for (var i = 0; i < 1; i++) {
//           const now = new Date().getTime();
//           console.log( now );

//           console.log('Clicked Start Record')
//           await device_manager.start_recording_download((success, data) => {
//             const now2 = new Date().getTime();
//             console.log( now2 );
//             console.log(data)
//             let blob = new Blob([data]);

//             let formData = new FormData();
//             formData.append('recording', blob, 'data.bin')
//             console.log(formData)
//             var obj = {
//               link: 'http://localhost:8000' + '/token',
//               object: {
//                 method: 'POST',
//                 headers: {
//                   "Content-Type": "application/x-www-form-urlencoded"
//                 },
//                 body: 'username=' + 'test' + '&password=' + 'test'
//               }
//             }
//             fetch(obj.link, obj.object).then(async response => {
//               const tokenResponse = (await response.json());
//               const token = tokenResponse?.access_token;
//               const obj = {
//                 link: 'http://localhost:8001/recording',
//                 object: {
//                   method: 'POST',
//                   headers: {
//                     'Authorization': 'Bearer ' + token,
//                   },
//                   body: formData
//                 }
//               };
//               fetch(obj.link, obj.object);
//               // TODO add bad response
//             })
//             console.log('Download Complete');
//             console.log(success);
//             // TODO compute the hash of the received bytes
//           });

//         }
//       }
//     }>StartDownload</button>
//   </>

//   // Download Button
//   // Login Button
//   // Upload Button

// }



// Login Page


// TODO do this differently

const tabBarStyles = StyleSheet.create({
  tabStyle: {
    display: "block",
    textDecoration: "none",
    padding: "10px",
    color: "#333",
    backgroundColor: "#e0e0e0",
    ":hover": {
      backgroundColor: "#b0b0b0",
    },
  },

  barStyle: {
    backgroundColor: "#f0f0f0",
    // width: "300px",
    padding: "20px",
    height: "100vh",
    // position: "fixed",
    maxWidth: 300,
    flex: 1
  },
})
// const TabBarContainer = styled.div`
//   background-color: #f0f0f0;
//   width: 200px;
//   padding: 20px;
//   height: 100%;
//   position: fixed;
// `;

// const Tab = styled(Link)`
//   display: block;
//   text-decoration: none;
//   padding: 10px;
//   color: #333;

//   &:hover {
//     background-color: #e0e0e0;
//   }
// `;

const TabBarContainer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <div className={css(tabBarStyles.barStyle)}>{children}</div>
}


const Tab: React.FC<{ to: string, children: React.ReactNode }> = ({ to, children }) => {
  return <Link to={to} className={css(tabBarStyles.tabStyle)}>{children}</Link>
}


function App() {
  const connectedDeviceAtomState = useRecoilValue(connectedDeviceAtom);
  const readingsAtomVal = useRecoilValue(readingsAtom);
  const recordingStateAtomVal = useRecoilValue(recordingStateAtom);
  const downloadStateAtomVal = useRecoilValue(downloadStateAtom);

  const authAtomVal = useRecoilValue(authAtom)

  if (authAtomVal.loggedIn) {
    return <>
      <Router>
        <div style={{display: "flex", height: "100%"}}>
        <TabBarContainer>
          <Tab to="/">Home</Tab>
          <Tab to="/account">Account</Tab>

          <Button style={{position: 'absolute', bottom: 20}} onClick={authManager.logout}>Logout</Button>

        </TabBarContainer>
        <div style={{flex: 4}}>
        <Routes>
          <Route path="/" element={<MainPage></MainPage>}>
          </Route>
          <Route path="/account">
            {/* <Account /> */}
          </Route>
        </Routes>
        </div>
        </div>
      </Router>
    </>
  } else {
    return <LoginPage></LoginPage>
  }

}


export default App;
