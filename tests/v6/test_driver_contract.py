from src.v6.hardware.instrument_interface import InstrumentInterface
from src.v6.hardware.serial_instrument import SerialInstrument
from src.v6.hardware.usb_instrument import USBInstrument


def test_serial_driver_implements_instrument_interface():
    instrument = SerialInstrument("COM_TEST")

    assert isinstance(instrument, InstrumentInterface)


def test_usb_driver_implements_instrument_interface():
    instrument = USBInstrument("USB_TEST_001")

    assert isinstance(instrument, InstrumentInterface)