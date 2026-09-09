import socket

import pytest

from src.v6.hardware.device_discovery import (
    create_tcp_device_descriptor,
    create_usb_device_descriptor,
    discover_local_hardware,
    discover_serial_devices,
    validate_tcp_endpoint,
)


def test_discover_serial_devices_returns_list():
    devices = discover_serial_devices()

    assert isinstance(devices, list)

    for device in devices:
        assert "port" in device
        assert "description" in device
        assert "hardware_id" in device


def test_local_hardware_discovery_structure():
    result = discover_local_hardware()

    assert "serial_devices" in result
    assert "usb_devices" in result
    assert "tcp_devices" in result

    assert isinstance(
        result["serial_devices"],
        list,
    )

    assert isinstance(
        result["usb_devices"],
        list,
    )

    assert isinstance(
        result["tcp_devices"],
        list,
    )


def test_valid_tcp_endpoint():
    assert validate_tcp_endpoint(
        "127.0.0.1",
        5000,
    ) is True


def test_invalid_tcp_port():
    with pytest.raises(
        ValueError,
        match="port must be between",
    ):
        validate_tcp_endpoint(
            "127.0.0.1",
            70000,
        )


def test_empty_tcp_host():
    with pytest.raises(
        ValueError,
        match="host cannot be empty",
    ):
        validate_tcp_endpoint(
            "",
            5000,
        )


def test_usb_descriptor():
    device = create_usb_device_descriptor(
        device_id="USB_TEST_001",
        description="Test Gas Analyzer",
        manufacturer="Example Instruments",
        model="GA-500",
        serial_number="GA-500-001",
    )

    assert device["device_id"] == "USB_TEST_001"
    assert device["description"] == "Test Gas Analyzer"
    assert device["manufacturer"] == "Example Instruments"
    assert device["model"] == "GA-500"
    assert device["serial_number"] == "GA-500-001"


def test_usb_empty_id_rejected():
    with pytest.raises(
        ValueError,
        match="device_id cannot be empty",
    ):
        create_usb_device_descriptor(
            device_id="",
            description="Test Device",
        )


def test_tcp_descriptor():
    descriptor = create_tcp_device_descriptor(
        host="127.0.0.1",
        port=65534,
        timeout=0.1,
    )

    assert descriptor["host"] == "127.0.0.1"
    assert descriptor["port"] == 65534
    assert isinstance(
        descriptor["reachable"],
        bool,
    )


def test_tcp_invalid_host_rejected():
    with pytest.raises(ValueError):
        validate_tcp_endpoint(
            "this-host-should-not-exist-123456.invalid",
            5000,
        )