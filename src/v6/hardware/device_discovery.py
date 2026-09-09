"""
Physical Device Discovery
=========================

Safely discovers available hardware interfaces without opening,
modifying, or communicating with the devices.

Currently supports:
- Serial / COM ports
- TCP endpoint configuration validation
- USB-style device descriptors supplied by the application

This module performs discovery only. It does not claim that a
detected device is a laboratory instrument.
"""

from dataclasses import dataclass, asdict
from ipaddress import ip_address
import socket

import serial.tools.list_ports


@dataclass
class SerialDevice:
    port: str
    description: str
    manufacturer: str | None
    product: str | None
    serial_number: str | None
    hardware_id: str | None


@dataclass
class TCPDevice:
    host: str
    port: int
    reachable: bool


@dataclass
class USBDevice:
    device_id: str
    description: str
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None


def discover_serial_devices() -> list[dict]:
    """
    Discover currently visible COM/serial devices.

    No connection is opened.
    """

    devices = []

    for port_info in serial.tools.list_ports.comports():
        device = SerialDevice(
            port=port_info.device,
            description=port_info.description or "",
            manufacturer=port_info.manufacturer,
            product=port_info.product,
            serial_number=port_info.serial_number,
            hardware_id=port_info.hwid,
        )

        devices.append(asdict(device))

    return devices


def validate_tcp_endpoint(
    host: str,
    port: int,
) -> bool:
    """
    Validate TCP endpoint syntax without connecting to it.
    """

    if not host or not host.strip():
        raise ValueError("host cannot be empty.")

    if port < 1 or port > 65535:
        raise ValueError(
            "port must be between 1 and 65535."
        )

    normalized_host = host.strip()

    try:
        ip_address(normalized_host)
    except ValueError:
        try:
            socket.getaddrinfo(
                normalized_host,
                port,
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as exc:
            raise ValueError(
                f"Unable to resolve host: {normalized_host}"
            ) from exc

    return True


def check_tcp_reachability(
    host: str,
    port: int,
    timeout: float = 1.0,
) -> bool:
    """
    Check whether a TCP endpoint accepts a connection.

    This performs an actual network connection attempt.
    """

    if timeout <= 0:
        raise ValueError(
            "timeout must be greater than 0."
        )

    validate_tcp_endpoint(host, port)

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            return True
    except (OSError, TimeoutError):
        return False


def create_tcp_device_descriptor(
    host: str,
    port: int,
    timeout: float = 1.0,
) -> dict:
    """
    Create a structured TCP device descriptor.
    """

    validate_tcp_endpoint(host, port)

    reachable = check_tcp_reachability(
        host=host,
        port=port,
        timeout=timeout,
    )

    device = TCPDevice(
        host=host,
        port=port,
        reachable=reachable,
    )

    return asdict(device)


def create_usb_device_descriptor(
    device_id: str,
    description: str,
    manufacturer: str | None = None,
    model: str | None = None,
    serial_number: str | None = None,
) -> dict:
    """
    Create a structured USB device descriptor.

    Discovery metadata can come from an OS/device enumeration
    layer when a real USB instrument is available.
    """

    if not device_id or not device_id.strip():
        raise ValueError(
            "device_id cannot be empty."
        )

    if not description or not description.strip():
        raise ValueError(
            "description cannot be empty."
        )

    device = USBDevice(
        device_id=device_id.strip(),
        description=description.strip(),
        manufacturer=manufacturer,
        model=model,
        serial_number=serial_number,
    )

    return asdict(device)


def discover_local_hardware() -> dict:
    """
    Return all safely discoverable local hardware information.
    """

    return {
        "serial_devices": discover_serial_devices(),
        "usb_devices": [],
        "tcp_devices": [],
    }