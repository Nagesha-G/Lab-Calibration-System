from src.v6.hardware.driver_registry import create_instrument_driver
from src.v6.hardware.instrument_interface import InstrumentInterface


def test_create_simulated_driver():
    instrument = create_instrument_driver(
        "simulated",
        instrument_id=1,
    )

    assert isinstance(instrument, InstrumentInterface)
    assert instrument.instrument_id == 1


def test_create_serial_driver():
    instrument = create_instrument_driver(
        "serial",
        port="COM_TEST",
    )

    assert isinstance(instrument, InstrumentInterface)
    assert instrument.port == "COM_TEST"


def test_create_usb_driver():
    instrument = create_instrument_driver(
        "usb",
        device_id="USB_TEST_001",
    )

    assert isinstance(instrument, InstrumentInterface)
    assert instrument.device_id == "USB_TEST_001"


def test_create_tcp_driver():
    instrument = create_instrument_driver(
        "tcp",
        host="127.0.0.1",
        port=5000,
    )

    assert isinstance(instrument, InstrumentInterface)
    assert instrument.host == "127.0.0.1"
    assert instrument.port == 5000


def test_unsupported_driver_rejected():
    try:
        create_instrument_driver("unknown")
        assert False, "Unsupported driver should be rejected."
    except ValueError as exc:
        assert "Unsupported driver type" in str(exc)