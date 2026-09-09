import json
from pathlib import Path

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Lab Calibration System V6",
    page_icon="🔬",
    layout="wide",
)


def api_get(path, params=None):
    response = requests.get(
        f"{API_URL}{path}",
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def api_post(path, payload=None, params=None):
    response = requests.post(
        f"{API_URL}{path}",
        json=payload,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def api_delete(path):
    response = requests.delete(
        f"{API_URL}{path}",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def show_api_error(exc):
    if isinstance(exc, requests.exceptions.ConnectionError):
        st.error(
            "V6 API is not running. Start it with:\n\n"
            "`uvicorn src.v6.api.main:app --reload`"
        )
        return

    if isinstance(exc, requests.exceptions.HTTPError):
        try:
            detail = exc.response.json()
        except Exception:
            detail = exc.response.text

        st.error(f"API error: {detail}")
        return

    st.error(f"Unexpected error: {exc}")


def main():
    st.title("🔬 Lab Calibration System")
    st.caption("V6 Hardware-Integrated Calibration Platform")

    try:
        health = api_get("/health")
        api_online = health.get("status") == "healthy"
    except Exception:
        api_online = False
        health = {}

    if api_online:
        st.success("API Online")
    else:
        st.error("API Offline")

    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Select page",
        [
            "Dashboard",
            "Hardware Session",
            "Calibration History",
            "Calibration Summary",
            "Drivers",
        ],
    )

    if page == "Dashboard":
        dashboard_page()

    elif page == "Hardware Session":
        hardware_session_page()

    elif page == "Calibration History":
        calibration_history_page()

    elif page == "Calibration Summary":
        calibration_summary_page()

    elif page == "Drivers":
        drivers_page()


def dashboard_page():
    st.header("Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    try:
        summary = api_get(
            "/hardware/instruments/1/calibration-summary"
        )

        col1.metric(
            "Calibrations",
            summary["total_calibrations"],
        )

        col2.metric(
            "PASS",
            summary["pass_count"],
        )

        col3.metric(
            "FAIL",
            summary["fail_count"],
        )

        col4.metric(
            "Pass Rate",
            f'{summary["pass_rate"]:.2f}%',
        )

        st.subheader("Calibration Performance")

        st.write(
            {
                "Average Absolute Error":
                    summary["average_absolute_error"],
                "Pass Rate":
                    f'{summary["pass_rate"]:.2f}%',
            }
        )

    except Exception as exc:
        show_api_error(exc)


def hardware_session_page():
    st.header("Hardware Session")

    st.subheader("Create Session")

    driver_type = st.selectbox(
        "Driver",
        [
            "simulated",
            "serial",
            "usb",
            "tcp",
        ],
    )

    instrument_id = st.number_input(
        "Instrument ID",
        min_value=1,
        value=1,
        step=1,
    )

    model_id = st.number_input(
        "Model ID",
        min_value=1,
        value=5,
        step=1,
    )

    reference_value = st.number_input(
        "Reference Value",
        min_value=0.01,
        value=2.0,
        step=0.1,
    )

    driver_config = {}

    if driver_type == "simulated":
        driver_config = {
            "instrument_id": instrument_id
        }

    elif driver_type == "serial":
        port = st.text_input(
            "COM Port",
            value="COM3",
        )

        baudrate = st.number_input(
            "Baud Rate",
            min_value=1,
            value=9600,
            step=1,
        )

        timeout = st.number_input(
            "Timeout",
            min_value=0.1,
            value=2.0,
            step=0.1,
        )

        driver_config = {
            "port": port,
            "baudrate": baudrate,
            "timeout": timeout,
        }

    elif driver_type == "usb":
        device_id = st.text_input(
            "USB Device ID",
            value="USB_TEST_001",
        )

        driver_config = {
            "device_id": device_id,
        }

    elif driver_type == "tcp":
        host = st.text_input(
            "TCP Host",
            value="127.0.0.1",
        )

        port = st.number_input(
            "TCP Port",
            min_value=1,
            max_value=65535,
            value=5000,
            step=1,
        )

        timeout = st.number_input(
            "Timeout",
            min_value=0.1,
            value=2.0,
            step=0.1,
        )

        driver_config = {
            "host": host,
            "port": port,
            "timeout": timeout,
        }

    if st.button(
        "Create Hardware Session",
        type="primary",
    ):
        try:
            result = api_post(
                "/hardware/sessions",
                {
                    "driver_type": driver_type,
                    "instrument_id": instrument_id,
                    "model_id": model_id,
                    "reference_value": reference_value,
                    "driver_config": driver_config,
                },
            )

            st.session_state["hardware_session_id"] = (
                result["session_id"]
            )

            st.success("Hardware session created.")

            st.json(result)

        except Exception as exc:
            show_api_error(exc)

    session_id = st.session_state.get(
        "hardware_session_id"
    )

    if session_id:
        st.divider()

        st.subheader("Current Session")

        st.code(session_id)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Start Session"):
                try:
                    result = api_post(
                        f"/hardware/sessions/{session_id}/start"
                    )

                    st.success("Session started.")
                    st.json(result)

                except Exception as exc:
                    show_api_error(exc)

        with col2:
            if st.button("Calibrate Once"):
                try:
                    result = api_post(
                        f"/hardware/sessions/"
                        f"{session_id}/calibrate"
                    )

                    if result["status"] == "PASS":
                        st.success("Calibration PASS")
                    else:
                        st.warning("Calibration FAIL")

                    st.json(result)

                except Exception as exc:
                    show_api_error(exc)

        with col3:
            if st.button("Stop Session"):
                try:
                    result = api_post(
                        f"/hardware/sessions/"
                        f"{session_id}/stop"
                    )

                    st.info("Session stopped.")
                    st.json(result)

                except Exception as exc:
                    show_api_error(exc)

        st.subheader("Continuous Calibration")

        cycles = st.number_input(
            "Cycles",
            min_value=1,
            value=3,
            step=1,
        )

        interval = st.number_input(
            "Interval (seconds)",
            min_value=0.0,
            value=0.5,
            step=0.1,
        )

        if st.button("Run Calibration Cycles"):
            try:
                result = api_post(
                    f"/hardware/sessions/"
                    f"{session_id}/run",
                    params={
                        "number_of_cycles": cycles,
                        "interval_seconds": interval,
                    },
                )

                st.success(
                    f'Completed {result["cycles_completed"]} '
                    f'cycles.'
                )

                st.json(result)

            except Exception as exc:
                show_api_error(exc)

        if st.button("Delete Session"):
            try:
                result = api_delete(
                    f"/hardware/sessions/{session_id}"
                )

                st.info("Session deleted.")

                st.json(result)

                st.session_state.pop(
                    "hardware_session_id",
                    None,
                )

            except Exception as exc:
                show_api_error(exc)


def calibration_history_page():
    st.header("Calibration History")

    limit = st.number_input(
        "Records",
        min_value=1,
        max_value=500,
        value=20,
        step=1,
    )

    try:
        data = api_get(
            "/hardware/instruments/1/calibrations",
            params={"limit": limit},
        )

        st.metric(
            "Records",
            data["count"],
        )

        if data["records"]:
            st.dataframe(
                data["records"],
                use_container_width=True,
            )
        else:
            st.info("No calibration records found.")

    except Exception as exc:
        show_api_error(exc)


def calibration_summary_page():
    st.header("Calibration Summary")

    try:
        summary = api_get(
            "/hardware/instruments/1/calibration-summary"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total",
            summary["total_calibrations"],
        )

        col2.metric(
            "PASS",
            summary["pass_count"],
        )

        col3.metric(
            "FAIL",
            summary["fail_count"],
        )

        st.metric(
            "Pass Rate",
            f'{summary["pass_rate"]:.2f}%',
        )

        st.metric(
            "Average Absolute Error",
            summary["average_absolute_error"],
        )

    except Exception as exc:
        show_api_error(exc)


def drivers_page():
    st.header("Hardware Drivers")

    try:
        data = api_get("/hardware/drivers")

        for driver in data["drivers"]:
            st.success(driver.upper())

    except Exception as exc:
        show_api_error(exc)


if __name__ == "__main__":
    main()