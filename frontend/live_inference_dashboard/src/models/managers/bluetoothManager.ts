import { getRecoil, setRecoil } from "recoil-nexus";
import { MindFeedBluetoothDeviceManager } from "../../utils/BluetoothManager";
import { connectedDeviceAtom, downloadStateAtom, readingsAtom, recordingStateAtom } from "../atoms/bluetoothAtoms";



const bluetoothManager = {

    _deviceManager: new MindFeedBluetoothDeviceManager(

        (device: BluetoothDevice) => {
            setRecoil(connectedDeviceAtom, {
                device_name: device.name == undefined ? 'Na' : device.name,
                connected: device.gatt?.connected == undefined ? false : device.gatt?.connected
            });
        },

        () => {
            setRecoil(connectedDeviceAtom, {
                device_name: 'Na',
                connected: false,
            });
        }

    ),

    _setup: function () {
        // TODO create the bluetooth manager and set the callbacks relating setting atom states
        this._deviceManager.set_on_reading(
            (reading) => {
              setRecoil(readingsAtom, [...getRecoil(readingsAtom), reading])
            }
          );

          this._deviceManager.set_on_recording_state_change(
            (state) => {
              setRecoil(recordingStateAtom, state);
            }
          );

          this._deviceManager.set_on_download_state_change(
            (state) => {
              setRecoil(downloadStateAtom, state);
            }
          );

    },

    // TODO Connect to a device
    connect_device : function () {
        // TODO
    },

    disconnect_device : function () {
        // TODO
    },

    // TODO design
    record : function () {
        // TODO
    },

    // TODO add callback
    getRecording : function () {
        // TODO
    }

}
bluetoothManager._setup()

export default bluetoothManager;
