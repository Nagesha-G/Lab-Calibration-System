from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.usb_protocol import decode_usb_measurement


class USBInstrument(InstrumentInterface):
    """
    USB instrument driver abstraction.

    The concrete USB transport is intentionally abstracted so the
    same driver can later be connected to a real USB instrument.
    """

    def __init__(self, device_id: str):
        if not device_id or not device_id.strip():
            raise ValueError("device_id cannot be empty.")

        self.device_id = device_id
        self._connected = False
        self._device = None

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False
        self._device = None

    def is_connected(self) -> bool:
        return self._connected

    def read_measurement(self) -> dict:
        if not self.is_connected():
            raise RuntimeError(
                "USB instrument is not connected."
            )

        if self._device is None:
            raise RuntimeError(
                "USB device transport is not configured."
            )

        raw_data = self._device.read()

        if not raw_data:
            raise TimeoutError(
                "No measurement received from USB instrument."
            )

        return decode_usb_measurement(raw_data)