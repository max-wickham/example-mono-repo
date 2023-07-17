export enum RecordingState
{
    RSNotRecording = 0,
    RSInProgress,
    RSComplete,
}

export enum RecordingStateRequest
{
    RSRStartRequested = 0,
    RSRStopRequested,
}

export enum DownloadStateRequest
{
    DSRStartRequested = 0,
    DSRNotRequested,
}

export enum DownloadState
{
    DSStopped = 0,
    DSInProgress,
    DSComplete,
}

function intToArrayBuffer(num: number, size = 4): ArrayBuffer {
    const buffer = new ArrayBuffer(size); // An integer is 4 bytes
    const view = new DataView(buffer);
    view.setInt32(0, num, true); // Write the number starting at byte 0
    return buffer;
  }

const read_service_uuid = "99497f04-e714-476e-9f2b-087785ba0315";
const current_reading_characteristic_uuid = "8018a468-562c-4b09-9b7c-60935f0b26c4";
const recording_state_service_uuid = "2c6c0afb-030c-42d1-88e0-950616111bdc";
const recording_state_characteristic_uuid = "1fcdb326-0779-4aed-b50b-d0b21e00c277";
const recording_request_characteristic_uuid = "765c0ac1-ed04-48af-997a-dc56d3dad788";

const packet_size = 512;

export class MindFeedBluetoothDeviceManager {
    public device: BluetoothDevice | null = null;
    // To be called when connecting to a device
    private _on_connect: (device: BluetoothDevice) => void;
    // To be called when a device disconnects
    private _on_disconnect: () => void;
    // Callback when receiving a reading
    private _on_reading: (reading : number) => void = (_) => {};
    // Callback when recording state changed
    private _on_recording_state_change: (recording_state: RecordingState) => void = (_) => {};
    // Callback for download state change
    private _on_download_state_change: (download_state: DownloadState) => void = (_) => {};
    // Callback for when a download is complete
    private _on_download_complete: (recording_successful : boolean, recording : ArrayBuffer[]) => void = (_,__) => {};

    // Current recording state of the device
    private _recording_state: RecordingState = RecordingState.RSNotRecording;

    // Recording download states
    private _download_state: DownloadState = DownloadState.DSStopped;
    private _expected_recording_hash: number = 0;
    private _recording_download: ArrayBuffer[] = []

    // Characteristic used to write recording instructions to the device
    private _recording_request_characteristic: BluetoothRemoteGATTCharacteristic | null = null;

    // Characteristic used to write download instructions to the device
    private _download_request_characteristic: BluetoothRemoteGATTCharacteristic | null = null;

    constructor(on_connect : (device: BluetoothDevice) => void, on_disconnect : () => void) {
        this._on_connect = on_connect;
        this._on_disconnect = on_disconnect;
    }

    // Setters for the various callbacks
    set_on_reading(on_reading: (reading : number) => void){
        this._on_reading = on_reading;
    }

    set_on_recording_state_change(on_recording_state_change: (recording_state: RecordingState) => void){
        this._on_recording_state_change = on_recording_state_change;
    }

    set_on_download_state_change(_on_download_state_change: (download_state: DownloadState) => void){
        this._on_download_state_change = _on_download_state_change;
    }

    // Public methods

    request_start_recording() {
        // check that the recording state is not in progress
        if (this._recording_state == RecordingState.RSInProgress){
            return;
        }
        if(this._recording_request_characteristic == null || this.device == null){
            return;
        }
        // send the recording request
        this._recording_request_characteristic.writeValue(intToArrayBuffer(RecordingStateRequest.RSRStartRequested))
    }

    request_stop_recording() {
        // check that the recording state is in progress
        if (this._recording_state != RecordingState.RSInProgress){
            return;
        }
        if(this._recording_request_characteristic == null || this.device == null){
            return;
        }
        // send the recording request
        this._recording_request_characteristic.writeValue(intToArrayBuffer(RecordingStateRequest.RSRStopRequested))
    }

    start_recording_download(on_download_complete: (recording_successful : boolean, recording : ArrayBuffer[]) => void){
        // Download the recording and then call the callback function

        // check currently connected to a device
        if(this._download_request_characteristic == null || this.device == null){
            return;
        }
        // need the recording state to be complete
        if (this._recording_state != RecordingState.RSComplete){
            return;
        }

        // need download state not to be in progress
        if (this._download_state == DownloadState.DSInProgress){
            return;
        }

        this._on_download_complete = on_download_complete;

        // clear the buffer
        this._recording_download = [];
        // tell the device to start transmitting
        this._download_request_characteristic.writeValue(intToArrayBuffer(DownloadStateRequest.DSRStartRequested));
    }

    async connect() {
        console.log('Connecting to device')
        this.device = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: [read_service_uuid]
        });
        console.log('Paired to device')
        this._setupDevice();
    }

    private async _setupDevice() {
        console.log('Setting up device')
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


        ///////////// Setup the measurement reading characteristic

        const reading_service = await server.getPrimaryService(read_service_uuid);
        var current_reading_characteristic = await reading_service.getCharacteristic(current_reading_characteristic_uuid);
        // add the callback when a reading is received
        current_reading_characteristic.addEventListener('characteristicvaluechanged',(event) => {
            console.log('Reading')
            // @ts-ignore
            const reading : number = event.target.value.getInt32(0, true); // use little endian
            console.log(reading)
            this._on_reading(reading);
        });
        // start the notifications
        current_reading_characteristic.startNotifications().then(() => current_reading_characteristic);

        /////////////// Setup the recording state characteristic

        const recording_state_service = await server.getPrimaryService(recording_state_service_uuid);
        var recording_state_characteristic = await recording_state_service.getCharacteristic(recording_state_characteristic_uuid);
        this._recording_request_characteristic = await recording_state_service.getCharacteristic(recording_request_characteristic_uuid);

        recording_state_characteristic.addEventListener('characteristicvaluechanged',(event) => {
            console.log('Recording State Changed')
            // @ts-ignore
            const state : RecordingState = event.target.value.getInt32(0, true); // use little endian
            this._recording_state = state;
            this._on_recording_state_change(this._recording_state);
        });

        recording_state_characteristic.startNotifications();

        /////////////// Setup the recording downloading characteristics

        const recording_download_service = await server.getPrimaryService(recording_state_service_uuid);

        // one characteristic for requesting download, must be turned on then off
        this._download_request_characteristic = await recording_download_service.getCharacteristic(recording_state_characteristic_uuid);
        // one characteristic for stating download in process
        var download_state_progress_characteristic = await recording_download_service.getCharacteristic(recording_state_characteristic_uuid);
        // one characteristic for the final hash of the download
        var recording_hash_characteristic = await recording_download_service.getCharacteristic(recording_state_characteristic_uuid);
        // on characteristic for the bytes
        var tx_characteristic = await recording_download_service.getCharacteristic(recording_state_characteristic_uuid);

        download_state_progress_characteristic.addEventListener('characteristicvaluechanged',(event) => {
            console.log('Download State Changed')
            // @ts-ignore
            const state : DownloadState = event.target.value.getInt32(0, true); // use little endian
            this._download_state_change(state);
        });
        download_state_progress_characteristic.startNotifications();

        recording_hash_characteristic.addEventListener('characteristicvaluechanged',(event) => {
            console.log('Received Recording Hash')
            // @ts-ignore
            const hash : number = event.target.value.getInt32(0, true); // use little endian
            this._expected_recording_hash = hash;
        });
        recording_hash_characteristic.startNotifications();

        tx_characteristic.addEventListener('characteristicvaluechanged',(event) => {
            console.log('Received Recording Hash')
            // @ts-ignore
            const bytes : ArrayBuffer = event.target.value; // use little endian
            this._receive_tx_bytes(bytes)
        });
        tx_characteristic.startNotifications();



        this._on_connect(this.device)
    }

    private _download_state_change(download_state: DownloadState) {

        // if the recording has just finished
        if (this._download_state == DownloadState.DSInProgress && download_state == DownloadState.DSComplete){
            // handle the download complete process
            this._handle_download_complete();
        }
        // handle the change in download state
        this._download_state = download_state;

        this._on_download_state_change(this._download_state);
    }

    private _receive_tx_bytes(bytes: ArrayBuffer) {
        this._recording_download.push(bytes);
    }

    private _handle_download_complete() {
        // TODO check that the hash of the recorded bytes is what is expected

        const hash_correct = true;

        if(hash_correct){
            this._on_download_complete(true, this._recording_download);
        }
        else{
            this._on_download_complete(false, []);
        }
    }
}
