import { throws } from "assert";
import { Serializer } from "v8";


const PACKET_SIZE = 200;
// Server Characteristics
const SERVER_SERVICE = "b9908bbc-de94-42fb-952a-b4593d12ebd1"
const SERVER_MESSAGE = "99497f04-e714-476e-9f2b-087785ba0315"
const SERVER_CURRENT_ENDPOINT = "1fcdb326-0779-4aed-b50b-d0b21e00c277"
const SERVER_FILENAME = "80e11a85-32ff-4df0-b03b-6212b71d8f49"
// Client Characteristics
const CLIENT_SERVICE = "ce2bd191-c2b9-4e02-964c-0a0bd7e421da"
const CLIENT_MESSAGE = "b44c49de-4751-439c-8ea7-c3bc2516aa3c"
const CLIENT_CURRENT_ENDPOINT = "7f853ef2-ba92-4c0a-bf53-b7dd876f0153"
const CLIENT_RECEIVING = "58813e28-4aa6-4e99-abf7-d5f198cfd819"
const CLIENT_RX = "2aa577c5-a852-487c-8e01-1237a093a0be"


function delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function stringToAsciiArrayBuffer(inputString: string): ArrayBuffer {
    const buffer = new ArrayBuffer(inputString.length);
    const view = new Uint8Array(buffer);

    for (let i = 0; i < inputString.length; i++) {
        const charCode = inputString.charCodeAt(i);
        view[i] = charCode;
    }

    return buffer;
}

function asciiArrayBufferToString(buffer: ArrayBuffer): string {
    const view = new Uint8Array(buffer);
    let result = "";

    for (let i = 0; i < view.length; i++) {
        const charCode = view[i];
        result += String.fromCharCode(charCode);
    }

    return result;
}

function intToArrayBuffer(num: number, size = 4): ArrayBuffer {
    const buffer = new ArrayBuffer(size); // An integer is 4 bytes
    const view = new DataView(buffer);
    view.setInt32(0, num, true); // Write the number starting at byte 0
    return buffer;
}

function concatDataViews(dataViews: DataView[]): ArrayBuffer {
    // Convert each DataView to its underlying ArrayBuffer
    let buffers = dataViews.map(view => view.buffer);

    // Now we can use the same approach as before
    let totalLength = buffers.reduce((prev, curr) => prev + curr.byteLength, 0);
    let result = new Uint8Array(totalLength);
    let offset = 0;
    for (let buffer of buffers) {
        result.set(new Uint8Array(buffer), offset);
        offset += buffer.byteLength;
    }

    return result.buffer;
}

class Characteristic {

    private _characteristic: BluetoothRemoteGATTCharacteristic;
    private _service: BluetoothRemoteGATTService;

    constructor(service: BluetoothRemoteGATTService, characteristic: BluetoothRemoteGATTCharacteristic) {

        this._service = service;
        this._characteristic = characteristic;
    }

    // @ts-ignore
    static async construct_from_uuid(uuid: string, service: BluetoothRemoteGATTService): Promise<this> {
        const instance = new this(service, await service.getCharacteristic(uuid));
        return instance;
    }

    public add_callback(callback: (data: DataView) => Promise<void>) {
        this._characteristic.addEventListener('characteristicvaluechanged', (event) => {
            // @ts-ignore
            const bytes: DataView = event.target.value; // use little endian
            callback(bytes);
        });
        this._characteristic.startNotifications();
    }

    public async get_int_value(): Promise<number> {
        const value = (await this._characteristic.readValue()).getInt32(0, true); // use little endian
        return value;
    }

    public async set_value(value: ArrayBuffer) {
        this._characteristic.writeValue(value);
    }

    public async set_int_value(value: number) {
        this._characteristic.writeValue(intToArrayBuffer(value));
    }

    public async set_string_value(value: string) {
        console.log('Setting Value')
        await this.set_value(stringToAsciiArrayBuffer(value));
    }

    public async get_string_value() {
        return asciiArrayBufferToString(await (await this._characteristic.readValue()).buffer)
    }

}

export class BluetoothController {

    public device: BluetoothDevice | null = null;

    private _on_connect: (device: BluetoothDevice) => void;
    // To be called when a device disconnects
    private _on_disconnect: () => void;

    private _server_chars: {
        server_message: Characteristic,
        server_endpoint: Characteristic,
        server_filename: Characteristic,
    } | null = null;

    private _client_chars: {
        client_message: Characteristic,
        client_endpoint: Characteristic,
        client_receiving: Characteristic,
        client_rx: Characteristic,
    } | null = null;

    private _server_service: BluetoothRemoteGATTService | null = null;
    private _client_service: BluetoothRemoteGATTService | null = null;

    private _callbacks: { [endpoint: string]: (message: string) => Promise<void> } = {};

    private _download_state: {
        buffer: DataView[],
        filename: string,
        receiving: boolean,
        callback: (data: ArrayBuffer) => Promise<void>
    } = {
            buffer: [],
            filename: '',
            receiving: false,
            callback: async (_) => {}
        }


    private async _setup_server_characteristics() {
        if (this._server_service == null) {
            return;
        }
        this._server_chars = {
            server_message: await Characteristic.construct_from_uuid(SERVER_MESSAGE, this._server_service),
            server_endpoint: await Characteristic.construct_from_uuid(SERVER_CURRENT_ENDPOINT, this._server_service),
            server_filename: await Characteristic.construct_from_uuid(SERVER_FILENAME, this._server_service),
        };
    }

    private async _setup_client_characteristics() {
        if (this._client_service == null) {
            return;
        }
        this._client_chars = {
            client_message: await Characteristic.construct_from_uuid(CLIENT_MESSAGE, this._client_service),
            client_endpoint: await Characteristic.construct_from_uuid(CLIENT_CURRENT_ENDPOINT, this._client_service),
            client_receiving: await Characteristic.construct_from_uuid(CLIENT_RECEIVING, this._client_service),
            client_rx: await Characteristic.construct_from_uuid(CLIENT_RX, this._client_service),
        };
        this._client_chars.client_message.add_callback(
            async (data) => {
                if (this._client_chars == null) {
                    return
                }
                const endpoint = await this._client_chars?.client_endpoint.get_string_value();
                await this._callbacks[endpoint](asciiArrayBufferToString(data.buffer));
            }
        )
        this._client_chars.client_receiving.add_callback(
            async (data) => {
                const receiving = asciiArrayBufferToString(data.buffer) == "true";
                if (receiving) {
                    this._download_state.receiving = true;
                } else if (this._download_state.receiving) {
                    this._download_state.receiving = false;
                    await this._download_state.callback(concatDataViews(this._download_state.buffer));
                }
            }
        )
        this._client_chars.client_rx.add_callback(
            async (data) => {
                console.log('Recievinf data');
                console.log(data);
                this._download_state.buffer.push(data);
            }
        )

    }


    private async _setupDevice() {
        console.log('Setting up device');

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
        this.device.addEventListener('gattserverdisconnected', (_) => {
            this.device = null;
            this._on_disconnect();
        });


        // const services = await server.getPrimaryServices();
        this._server_service = await server.getPrimaryService(SERVER_SERVICE);
        this._client_service = await server.getPrimaryService(CLIENT_SERVICE);

        await this._setup_server_characteristics();
        await this._setup_client_characteristics();

        this._on_connect(this.device);
    }


    constructor(on_connect: (device: BluetoothDevice) => void, on_disconnect: () => void) {
        this._on_connect = on_connect;
        this._on_disconnect = on_disconnect;
    }

    public async connect() {
        console.log('Connecting to device')
        this.device = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: [
                SERVER_SERVICE,
                CLIENT_SERVICE,
            ]
        });
        console.log('Paired to device')
        this._setupDevice();
    }


    public async send_message(endpoint: string, message: string) {
        await this._server_chars?.server_endpoint.set_string_value(endpoint);
        delay(10);
        await this._server_chars?.server_message.set_string_value(message);
    }

    public async add_callback(endpoint: string, callback: (message: string) => Promise<void>) {
        this._callbacks[endpoint] = callback;
    }

    public async request_file(filename: string, callback: (data: ArrayBuffer) => Promise<void>) {
        if (this._download_state.receiving){
            return;
        }
        this._download_state.buffer = [];
        this._download_state.callback = callback;
        this._server_chars?.server_filename.set_string_value(filename);
    }


}
