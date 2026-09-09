import serial

from src.v6.hardware.serial_protocol import (
    encode_measurement,
    decode_measurement,
)


TEST_MEASUREMENT = {
    "PT08.S1(CO)": 1200,
    "PT08.S2(NMHC)": 1000,
    "PT08.S3(NOx)": 900,
    "PT08.S4(NO2)": 1100,
    "PT08.S5(O3)": 1000,
    "T": 20,
    "RH": 50,
    "AH": 1.0,
}


def main():
    with serial.serial_for_url(
        "loop://",
        baudrate=9600,
        timeout=2,
        write_timeout=2,
    ) as connection:

        message = encode_measurement(TEST_MEASUREMENT)

        connection.write(message)
        connection.flush()

        received = connection.readline()

        measurement = decode_measurement(received)

        print("Sent:", TEST_MEASUREMENT)
        print("Received:", measurement)

        if measurement == TEST_MEASUREMENT:
            print("Serial loopback test PASSED")
        else:
            print("Serial loopback test FAILED")


if __name__ == "__main__":
    main()