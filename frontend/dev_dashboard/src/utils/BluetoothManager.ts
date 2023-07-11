

const read_service_uuid = "4fafc201-1fb5-459e-8fcc-c5c9c331914b";
const current_reading_characteristic_uuid = "beb5483e-36e1-4688-b7f5-ea07361b26a8";

export class MindFeedBluetoothDeviceManager {
    device: BluetoothDevice | null = null;
    on_connect: (device: BluetoothDevice) => void;
    on_disconnect: () => void;

    on_reading: (reading : number) => void = () => {};

    constructor(on_connect : (device: BluetoothDevice) => void, on_disconnect : () => void) {
        this.on_connect = on_connect;
        this.on_disconnect = on_disconnect;
    }

    set_on_reading(on_reading: (reading : number) => void){
        this.on_reading = on_reading;
    }

    async connect() {
        this.device = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: [read_service_uuid]
        });
        this._setupDevice();
    }

    async _setupDevice() {
        if (this.device === null || this.device === undefined) {
            console.log('No Device Connected');
            return
        }
        const server = await this.device.gatt?.connect();
        if (server == undefined) {
            console.log('Error');
            return;
        }

        // add callback when disconnected from the device
        this.device.addEventListener('gattserverdisconnected', () => {
            this.on_disconnect()
        });


        ///////////// Setup the measurement reading characteristic
        const reading_service = await server.getPrimaryService(read_service_uuid);
        var current_reading_characteristic = await reading_service.getCharacteristic(current_reading_characteristic_uuid)
        // add the callback when a reading is received
        current_reading_characteristic.addEventListener('characteristicvaluechanged',(event) => {
            // @ts-ignore
            const reading : number = event.target.value.getUint16(0);
            this.on_reading(reading);
        });
        // start the notifications
        current_reading_characteristic.startNotifications().then(() => current_reading_characteristic);

        /////////////// Setup the recording state characteristic



        /////////////// Setup the recording downloading characteristics

    }
}
