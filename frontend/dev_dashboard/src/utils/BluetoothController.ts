import { Serializer } from "v8";


const PACKET_SIZE = 200;
// Server Characteristics
const SERVER_SERVICE = "b9908bbc-de94-42fb-952a-b4593d12ebd1"
const SERVER_STATE = "99497f04-e714-476e-9f2b-087785ba0315"
const SERVER_CURRENT_ENDPOINT = "1fcdb326-0779-4aed-b50b-d0b21e00c277"

// Client Characteristics
const CLIENT_SERVICE = "ce2bd191-c2b9-4e02-964c-0a0bd7e421da"
const CLIENT_STATE = "b44c49de-4751-439c-8ea7-c3bc2516aa3c"
const CLIENT_CURRENT_ENDPOINT = "7f853ef2-ba92-4c0a-bf53-b7dd876f0153"

// Common Characteristics
const COMMON_SERVICE = "18d55f53-142a-4f7a-9874-e70f8ff7e385"
const MESSAGE_LENGTH = "8018a468-562c-4b09-9b7c-60935f0b26c4"
const MESSAGE_HASH = "2c6c0afb-030c-42d1-88e0-950616111bdc"
const REQUEST_RETRANSMIT = "765c0ac1-ed04-48af-997a-dc56d3dad788"
const TX = "f45bb166-b718-4f3e-865c-c9804a06f6b5"
const RX = "4463d9f3-911d-424f-ab17-af0ebc9ef236"
const MESSAGE_ID = "b66dca04-4a62-4367-b854-6b511ce903d1"


export interface File {
    length: number,
    bytes: ArrayBuffer
}

enum ClientServerState {
    Idle = 0,
    Transmitting,
    Receiving,
    Processing,
};

// function add_event_callback(characteristic: BluetoothRemoteGATTCharacteristic, callback: (event: Event) => void) {
//     characteristic.addEventListener('characteristicvaluechanged', (event) => {
//         callback(event);
//     });
//     characteristic.startNotifications();
// }

// function add_int_callback(characteristic: BluetoothRemoteGATTCharacteristic, callback: (value: number) => void) {
//     characteristic.addEventListener('characteristicvaluechanged', (event) => {
//         // @ts-ignore
//         const reading: number = event.target.value.getInt32(0, true);
//         callback(reading);
//     });
//     characteristic.startNotifications();
// }

// function add_string_callback(characteristic: BluetoothRemoteGATTCharacteristic, callback: (value: string) => void) {
//     characteristic.addEventListener('characteristicvaluechanged', (event) => {
//         // @ts-ignore
//         const reading: number = event.target.value.getInt32(0, true);
//         callback(reading);
//     });
//     characteristic.startNotifications();
// }

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
        this.set_value(stringToAsciiArrayBuffer(value));
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

    private _route_callbacks: { [route: string]: (message: string) => void } = {};

    private _server_chars: {
        server_state: Characteristic,
        server_endpoint: Characteristic,
    } | null = null;

    private _client_chars: {
        client_state: Characteristic,
        client_endpoint: Characteristic,
    } | null = null;

    private _common_chars: {
        message_length: Characteristic,
        message_hash: Characteristic,
        request_retransmit: Characteristic,
        tx: Characteristic,
        rx: Characteristic,
        message_id: Characteristic,
    } | null = null;

    private _server_service: BluetoothRemoteGATTService | null = null;
    private _client_service: BluetoothRemoteGATTService | null = null;
    private _common_service: BluetoothRemoteGATTService | null = null;


    private async _setup_server_characteristics() {
        if (this._server_service == null) {
            return;
        }
        this._server_chars = {
            server_state: await Characteristic.construct_from_uuid(SERVER_STATE, this._server_service),
            server_endpoint: await Characteristic.construct_from_uuid(SERVER_STATE, this._server_service),
        };
    }

    private async _setup_client_characteristics() {
        if (this._client_service == null) {
            return;
        }
        this._client_chars = {
            client_state: await Characteristic.construct_from_uuid(CLIENT_STATE, this._client_service),
            client_endpoint: await Characteristic.construct_from_uuid(CLIENT_CURRENT_ENDPOINT, this._client_service),
        };
    }

    private async _setup_common_characteristics() {
        if (this._common_service == null) {
            return;
        }
        this._common_chars = {
            message_length: await Characteristic.construct_from_uuid(MESSAGE_LENGTH, this._common_service),
            message_hash: await Characteristic.construct_from_uuid(MESSAGE_HASH, this._common_service),
            request_retransmit: await Characteristic.construct_from_uuid(REQUEST_RETRANSMIT, this._common_service),
            tx: await Characteristic.construct_from_uuid(TX, this._common_service),
            rx: await Characteristic.construct_from_uuid(RX, this._common_service),
            message_id: await Characteristic.construct_from_uuid(MESSAGE_ID, this._common_service),
        }
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
        this._common_service = await server.getPrimaryService(COMMON_SERVICE);

        await this._setup_server_characteristics();
        await this._setup_client_characteristics();
        await this._setup_common_characteristics();

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
                COMMON_SERVICE,
            ]
        });
        console.log('Paired to device')
        this._setupDevice();
    }

    private async _message_setup(route: string, message_length: number) {
        if (this._common_chars == null || this._client_chars == null || this._server_chars == null) {
            return;
        }
        const server_state: ClientServerState = await this._server_chars.server_state.get_int_value();
        if (server_state == ClientServerState.Processing || server_state == ClientServerState.Transmitting) {
            return;
        }
        await this._client_chars.client_state.set_int_value(ClientServerState.Transmitting);
        await this._client_chars.client_endpoint.set_string_value(route);
        await this._common_chars.message_length.set_int_value(message_length);
        // The message id change is what tells the server a message is about to be sent
        const message_id = await this._common_chars.message_id.get_int_value() + 1;
        await this._common_chars.message_id.set_int_value(message_id);
        // TODO add a timeout here
        while (true) {
            const server_state: ClientServerState = await this._server_chars.server_state.get_int_value();
            const server_endpoint = await this._server_chars.server_endpoint.get_string_value();
            if (server_endpoint === route && server_state === ClientServerState.Receiving) {
                break;
            }
            // poll every 20ms
            await delay(20);
        }
        return true;
    }

    private async _receive_text_response(): Promise<string> {
        if (this._common_chars == null || this._client_chars == null || this._server_chars == null) {
            return '';
        }
        // TODO
        while (true) {
            const server_state: ClientServerState = await this._server_chars.server_state.get_int_value();
            if (server_state == ClientServerState.Transmitting) {
                break;
            }
            await delay(20);
        }
        const response = this._common_chars.tx.get_string_value();
        return response;
    }

    // private async _receive_file_response() : Promise<File> {
    //     // TODO
    //     return '';
    // }

    public async send_message(route: string, message: string): Promise<string | File> {
        this._common_chars?.rx.set_string_value(message);
        const setup_success = await this._message_setup(route, message.length);
        return await this._receive_text_response();
    }

    // public async send_file (route: string, file: File) : Promise<string> {
    //     const setup_success = await this._message_setup(route, file.length);
    //     for (var i = 0; i < file.bytes.byteLength; i += PACKET_SIZE){
    //         this._common_chars?.rx.set_value(file.bytes.slice(i, i+ PACKET_SIZE));
    //     }
    //     // TODO send the file in packets over the rx line
    //     return await this._receive_text_response();
    // }

    // public add_route(route: string, callback: (message: string) => void) : void {
    //     this._route_callbacks[route] = callback;
    // }

}
