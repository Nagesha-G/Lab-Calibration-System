import pytest

from src.v6.hardware.configured_driver_factory import (
    create_configured_driver,
)
from src.v6.hardware.instrument_config import InstrumentConfig
from src.v6.hardware.instrument_adapter import InstrumentAdapter


def test_create_serial_configured_driver():
    config = InstrumentConfig(
        manufacturer="Example",
        model="GA-100",
        serial_number="TEST-001",
        transport_type="serial",
        read_command="MEAS?",
        connection={
            "port": "COM_TEST",
        },
        measurement_fields=["T"],
    )

    driver = create_configured_driver(config)

    assert isinstance(driver, InstrumentAdapter)
    assert driver.identity["manufacturer"] == "Example"


def test_create_usb_configured_driver():
    config = InstrumentConfig(
        manufacturer="Example",
        model="USB-GA",
        serial_number="USB-001",
        transport_type="usb",
        read_command="MEAS?",
        connection={
            "device_id": "USB_TEST_001",
        },
        measurement_fields=["T"],
    )

    driver = create_configured_driver(config)

    assert isinstance(driver, InstrumentAdapter)


def test_create_tcp_configured_driver():
    config = InstrumentConfig(
        manufacturer="Example",
        model="TCP-GA",
        serial_number="TCP-001",
        transport_type="tcp",
        read_command="MEAS?",
        connection={
            "host": "127.0.0.1",
            "port": 5000,
        },
        measurement_fields=["T"],
    )

    driver = create_configured_driver(config)

    assert isinstance(driver, InstrumentAdapter)