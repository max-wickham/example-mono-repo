import './App.css';
import { css } from 'aphrodite';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import {
  useRecoilState,
  useRecoilValue,
  useSetRecoilState,
} from 'recoil';
import { connectedDeviceAtom, readingsAtom } from './models/atoms';
import { getRecoil, setRecoil } from 'recoil-nexus';
import { MindFeedBluetoothDeviceManager } from './utils/BluetoothManager'


const device_manager = new MindFeedBluetoothDeviceManager(
  (device : BluetoothDevice) => {
    setRecoil(connectedDeviceAtom, {
      device_name: device.name == undefined ? 'Na' : device.name,
      connected: device.gatt?.connected == undefined ? false : device.gatt?.connected
    });
  },
  () => {}
)

// if (bluetoothDevice.gatt.connected && batteryLevelCharacteristic) {
//   return Promise.resolve();
// }

// log('Connecting to GATT Server...');
// return bluetoothDevice.gatt.connect()
// .then(server => {
//   log('Getting Battery Service...');
//   return server.getPrimaryService('battery_service');
// })
// .then(service => {
//   log('Getting Battery Level Characteristic...');
//   return service.getCharacteristic('battery_level');
// })
// .then(characteristic => {
//   batteryLevelCharacteristic = characteristic;
//   batteryLevelCharacteristic.addEventListener('characteristicvaluechanged',
//       handleBatteryLevelChanged);
//   document.querySelector('#startNotifications').disabled = false;
//   document.querySelector('#stopNotifications').disabled = true;
// });


async function setUpBluetoothDevice(device: BluetoothDevice) {
  // const server = await device.gatt?.connect();
  // if (server == undefined) {
  //   console.log('Error');
  //   return;
  // }
  // setRecoil(connectedDeviceAtom, {
  //   device_name: device.name == undefined ? 'Na' : device.name,
  //   connected: device.gatt?.connected == undefined ? false : device.gatt?.connected
  // });
  device.addEventListener('gattserverdisconnected', () => {
    setRecoil(connectedDeviceAtom, {
      device_name: 'None',
      connected: false,
    });
  });

  const reading_service = await server.getPrimaryService("4fafc201-1fb5-459e-8fcc-c5c9c331914b");

  const characteristics = await reading_service.getCharacteristics();
  console.log(characteristics);

  var current_reading_characteristic = await reading_service.getCharacteristic("beb5483e-36e1-4688-b7f5-ea07361b26a8")
  current_reading_characteristic.addEventListener('characteristicvaluechanged',(event) => {
    console.log('received value')
    // @ts-ignore
    const reading = event.target.value.getUint16(0);
    setRecoil(readingsAtom, [...getRecoil(readingsAtom), reading as number]);
  });
  current_reading_characteristic.startNotifications().then(() => current_reading_characteristic);

}

function ConnectToDeviceButton() {
  const setConnectedDeviceAtom = useSetRecoilState(connectedDeviceAtom);

  return <>
    <button onClick={
      async () => {
        await device_manager.connect()
        // @ts-ignore
        // const device = await navigator.bluetooth.requestDevice({
        //   acceptAllDevices: true,
        //   optionalServices: ["4fafc201-1fb5-459e-8fcc-c5c9c331914b"]
        // });

        // const device: BluetoothDevice = await navigator.bluetooth.requestDevice({
        //   filters:[
        //     {
        //       name: 'MindFeed'
        //     }
        //   ]
        // });

        // if (device != null && device != undefined) {
        //   setUpBluetoothDevice(device);
        // }
      }
    }>Test</button>
  </>
}

function App() {
  const connectedDeviceAtomState = useRecoilValue(connectedDeviceAtom);
  const readingsAtomState = useRecoilValue(readingsAtom);

  return <>
    <h1>Current Reading: {readingsAtomState.slice(-1)}</h1>
    <h1>Connected Device Name: {connectedDeviceAtomState == null ? '' : connectedDeviceAtomState.device_name}</h1>
    <ConnectToDeviceButton></ConnectToDeviceButton>
  </>
}


export default App;
