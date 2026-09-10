import requests
import streamlit as st

from pathlib import Path
import pandas as pd


API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Lab Calibration System",
    page_icon="🔬",
    layout="wide",
)


# ============================================================
# API HELPERS
# ============================================================

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

# ============================================================
# AUTHENTICATION
# ============================================================

def login_page():
    st.title("🔐 Lab Calibration System")
    st.subheader("Login")

    username = st.text_input(
        "Username",
        key="login_username",
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password",
    )

    if st.button(
        "Login",
        type="primary",
        width="stretch",
    ):
        if not username.strip() or not password:
            st.warning(
                "Username and password are required."
            )
            return

        try:
            result = api_post(
                "/login",
                {
                    "username": username,
                    "password": password,
                },
            )

            st.session_state["authenticated"] = True
            st.session_state["user_id"] = result["user_id"]
            st.session_state["username"] = result["username"]
            st.session_state["user_role"] = result["role"]

            st.success(
                f'Welcome, {result["username"]}.'
            )

            st.rerun()

        except Exception as exc:
            show_api_error(exc)


def show_api_error(exc):
    if isinstance(exc, requests.exceptions.ConnectionError):
        st.error(
            "V6 API is not running.\n\n"
            "Start it with:\n\n"
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


# ============================================================
# DASHBOARD
# ============================================================

def dashboard_page():
    st.header("🔬 Dashboard")
    st.caption("Lab Calibration System — Unified V6 Platform")

    try:
        health = api_get("/health")

        if health.get("status") == "healthy":
            st.success("V6 API Online")

    except Exception as exc:
        show_api_error(exc)
        return

    try:
        instruments = api_get("/instruments")
        models = api_get("/models/approved")

        instrument_count = instruments.get("count", 0)
        model_count = models.get("count", 0)

        summary = api_get(
            "/hardware/instruments/1/calibration-summary"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Instruments",
            instrument_count,
        )

        col2.metric(
            "Approved Models",
            model_count,
        )

        col3.metric(
            "Calibrations",
            summary["total_calibrations"],
        )

        col4.metric(
            "Pass Rate",
            f'{summary["pass_rate"]:.2f}%',
        )

        st.divider()

        st.subheader("Calibration Performance")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "PASS",
            summary["pass_count"],
        )

        col2.metric(
            "FAIL",
            summary["fail_count"],
        )

        col3.metric(
            "Average Absolute Error",
            summary["average_absolute_error"],
        )

    except Exception as exc:
        show_api_error(exc)


# ============================================================
# INSTRUMENTS
# ============================================================

def instruments_page():
    st.header("🏭 Instruments")

    try:
        data = api_get("/instruments")
        instruments = data.get("instruments", [])

        if not instruments:
            st.info("No instruments registered.")
            return

        st.subheader("Instrument Registry")

        st.dataframe(
            instruments,
            width="stretch",
        )

        instrument_ids = [
            instrument["instrument_id"]
            for instrument in instruments
        ]

        selected_id = st.selectbox(
            "Select Instrument",
            instrument_ids,
        )

        instrument = api_get(
            f"/instruments/{selected_id}"
        )

        st.subheader("Instrument Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                {
                    "ID": instrument["instrument_id"],
                    "Name": instrument["name"],
                    "Manufacturer": instrument["manufacturer"],
                    "Model": instrument["model"],
                    "Serial Number": instrument["serial_number"],
                }
            )

        with col2:
            st.write(
                {
                    "Instrument Type": instrument[
                        "instrument_type"
                    ],
                    "Status": instrument["status"],
                    "Created": instrument["created_at"],
                }
            )

        st.divider()

        st.subheader("Configuration")

        configurations = api_get(
            f"/instruments/{selected_id}/configurations"
        )

        if configurations["count"] > 0:
            st.dataframe(
                configurations["configurations"],
                width="stretch",
            )
        else:
            st.info("No configurations found.")

        st.subheader("Calibration Policy")

        policies = api_get(
            f"/instruments/{selected_id}/policies"
        )

        if policies["count"] > 0:
            st.dataframe(
                policies["policies"],
                width="stretch",
            )
        else:
            st.info("No calibration policies found.")

    except Exception as exc:
        show_api_error(exc)


# ============================================================
# CALIBRATION
# ============================================================

def calibration_page():
    st.header("⚙️ Calibration")

    try:
        instruments = api_get("/instruments")
        models = api_get("/models/approved")

        instrument_list = instruments.get(
            "instruments",
            [],
        )

        model_list = models.get(
            "models",
            [],
        )

        if not instrument_list:
            st.warning("No instruments available.")
            return

        if not model_list:
            st.warning("No approved models available.")
            return

        instrument_options = {
            (
                f'{item["instrument_id"]} — '
                f'{item["name"]} '
                f'({item["serial_number"]})'
            ): item["instrument_id"]
            for item in instrument_list
        }

        model_options = {
            (
                f'{item["model_id"]} — '
                f'{item["model_name"]} '
                f'v{item["model_version"]}'
            ): item["model_id"]
            for item in model_list
        }

        selected_instrument = st.selectbox(
            "Instrument",
            list(instrument_options.keys()),
        )

        instrument_id = instrument_options[
            selected_instrument
        ]

        selected_model = st.selectbox(
            "Approved Model",
            list(model_options.keys()),
        )

        model_id = model_options[selected_model]

        reference_value = st.number_input(
            "Reference Value",
            min_value=0.01,
            value=2.0,
            step=0.1,
        )

        st.divider()

        st.subheader("Hardware Session")

        driver_type = st.selectbox(
            "Driver",
            [
                "simulated",
                "serial",
                "usb",
                "tcp",
            ],
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

                st.session_state[
                    "hardware_session_id"
                ] = result["session_id"]

                st.success(
                    "Hardware session created."
                )

                st.json(result)

            except Exception as exc:
                show_api_error(exc)

        session_id = st.session_state.get(
            "hardware_session_id"
        )

        if not session_id:
            return

        st.divider()

        st.subheader("Current Session")

        st.code(session_id)

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button("Start Session"):

                try:

                    result = api_post(
                        f"/hardware/sessions/"
                        f"{session_id}/start"
                    )

                    st.success(
                        "Session started."
                    )

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
                        st.success(
                            "Calibration PASS"
                        )
                    else:
                        st.warning(
                            "Calibration FAIL"
                        )

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

                    st.info(
                        "Session stopped."
                    )

                    st.json(result)

                except Exception as exc:
                    show_api_error(exc)

        st.divider()

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

        if st.button(
            "Run Calibration Cycles"
        ):

            try:

                result = api_post(
                    f"/hardware/sessions/"
                    f"{session_id}/run",
                    params={
                        "number_of_cycles": int(
                            cycles
                        ),
                        "interval_seconds": float(
                            interval
                        ),
                    },
                )

                st.success(
                    f'Completed '
                    f'{result["cycles_completed"]} '
                    f'cycles.'
                )

                st.json(result)

            except Exception as exc:
                show_api_error(exc)

        if st.button("Delete Session"):

            try:

                result = api_delete(
                    f"/hardware/sessions/"
                    f"{session_id}"
                )

                st.info(
                    "Session deleted."
                )

                st.json(result)

                st.session_state.pop(
                    "hardware_session_id",
                    None,
                )

            except Exception as exc:
                show_api_error(exc)

    except Exception as exc:
        show_api_error(exc)


# ============================================================
# HISTORY
# ============================================================
def history_page():
    st.header("📜 Calibration History")

    try:
        instruments = api_get("/instruments")

        instrument_list = instruments.get(
            "instruments",
            [],
        )

        if not instrument_list:
            st.info("No instruments available.")
            return

        options = {
            (
                f'{item["instrument_id"]} — '
                f'{item["name"]}'
            ): item["instrument_id"]
            for item in instrument_list
        }

        selected = st.selectbox(
            "Instrument",
            list(options.keys()),
        )

        instrument_id = options[selected]

        limit = st.number_input(
            "Records",
            min_value=1,
            max_value=500,
            value=20,
            step=1,
        )

        data = api_get(
            f"/hardware/instruments/"
            f"{instrument_id}/calibrations",
            params={
                "limit": int(limit)
            },
        )

        st.metric(
            "Records",
            data["count"],
        )

        records = data.get(
            "records",
            [],
        )

        if records:
            st.dataframe(
                records,
                width="stretch",
            )

            # ====================================================
            # PDF CALIBRATION REPORT
            # ====================================================

            st.divider()

            st.subheader("📄 Calibration PDF Report")

            record_options = {
                f'Record {record["record_id"]} — '
                f'{record.get("status", "UNKNOWN")}': record["record_id"]
                for record in records
            }

            selected_record_label = st.selectbox(
                "Select calibration record",
                list(record_options.keys()),
                key="pdf_record_selector",
            )

            selected_record_id = record_options[
                selected_record_label
            ]

            st.write(
                f"Generate a PDF report for calibration "
                f"record **{selected_record_id}**."
            )

            if st.button(
                "Generate PDF Report",
                type="primary",
                key="generate_pdf_report",
            ):
                try:
                    response = requests.get(
                        f"{API_URL}/instruments/"
                        f"{instrument_id}/calibrations/"
                        f"{selected_record_id}/report",
                        timeout=30,
                    )

                    response.raise_for_status()

                    st.download_button(
                        "⬇️ Download Calibration PDF",
                        data=response.content,
                        file_name=(
                            f"calibration_report_"
                            f"instrument_{instrument_id}_"
                            f"record_{selected_record_id}.pdf"
                        ),
                        mime="application/pdf",
                        width="stretch",
                        key="download_calibration_pdf",
                    )

                    st.success(
                        "Calibration PDF generated successfully."
                    )

                except requests.RequestException as exc:
                    st.error(
                        f"Could not generate PDF report: {exc}"
                    )

        else:
            st.info(
                "No calibration records found."
            )

    except Exception as exc:
        show_api_error(exc)

# ============================================================
# SUMMARY
# ============================================================

def summary_page():
    st.header("📊 Calibration Summary")

    try:

        instruments = api_get(
            "/instruments"
        )

        instrument_list = instruments.get(
            "instruments",
            [],
        )

        if not instrument_list:
            st.info(
                "No instruments available."
            )
            return

        options = {
            (
                f'{item["instrument_id"]} — '
                f'{item["name"]}'
            ): item["instrument_id"]
            for item in instrument_list
        }

        selected = st.selectbox(
            "Instrument",
            list(options.keys()),
        )

        instrument_id = options[selected]

        summary = api_get(
            f"/hardware/instruments/"
            f"{instrument_id}/calibration-summary"
        )

        col1, col2, col3, col4 = st.columns(4)

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

        col4.metric(
            "Pass Rate",
            f'{summary["pass_rate"]:.2f}%',
        )

        st.metric(
            "Average Absolute Error",
            summary["average_absolute_error"],
        )

    except Exception as exc:
        show_api_error(exc)


# ============================================================
# USER MANAGEMENT
# ============================================================

def users_page():
    st.header("👥 User Management")

    # --------------------------------------------------------
    # Create User
    # --------------------------------------------------------

    st.subheader("Create User")

    col1, col2 = st.columns(2)

    with col1:
        username = st.text_input(
            "Username",
            key="new_username",
        )

        email = st.text_input(
            "Email",
            key="new_email",
        )

    with col2:
        password = st.text_input(
            "Password",
            type="password",
            key="new_password",
        )

        role = st.selectbox(
            "Role",
            [
                "operator",
                "admin",
            ],
            key="new_role",
        )

    if st.button(
        "Create User",
        type="primary",
    ):
        if not username.strip():
            st.warning("Username is required.")
            return

        if not email.strip():
            st.warning("Email is required.")
            return

        if not password:
            st.warning("Password is required.")
            return

        try:
            result = api_post(
                "/users",
                {
                    "username": username,
                    "email": email,
                    "password": password,
                    "role": role,
                },
            )

            st.success(
                f'User "{result["username"]}" created successfully.'
            )

            st.json(result)

        except Exception as exc:
            show_api_error(exc)

    st.divider()

    # --------------------------------------------------------
    # User Lookup
    # --------------------------------------------------------

    st.subheader("User Information")

    user_id = st.number_input(
        "User ID",
        min_value=1,
        value=1,
        step=1,
        key="lookup_user_id",
    )

    if st.button(
        "Load User",
        key="load_user",
    ):
        try:
            result = api_get(
                f"/users/{int(user_id)}"
            )

            st.json(result)

        except Exception as exc:
            show_api_error(exc)

    st.divider()

    # --------------------------------------------------------
    # Deactivate User
    # --------------------------------------------------------

    st.subheader("Deactivate User")

    deactivate_id = st.number_input(
        "User ID to deactivate",
        min_value=1,
        value=1,
        step=1,
        key="deactivate_user_id",
    )

    if st.button(
        "Deactivate User",
        key="deactivate_user",
    ):
        try:
            result = api_post(
                f"/users/{int(deactivate_id)}/deactivate"
            )

            st.success(
                f'User "{result["username"]}" is now inactive.'
            )

            st.json(result)

        except Exception as exc:
            show_api_error(exc)


# ============================================================
# MODELS
# ============================================================

def models_page():
    st.header("🤖 Model Management")

    # ========================================================
    # REGISTER MODEL
    # ========================================================

    st.subheader("Register Model")

    col1, col2 = st.columns(2)

    with col1:
        model_name = st.text_input(
            "Model Name",
            key="model_name",
        )

        model_version = st.text_input(
            "Model Version",
            value="1.0.0",
            key="model_version",
        )

        instrument_type = st.text_input(
            "Instrument Type",
            value="gas_analyzer",
            key="model_instrument_type",
        )

    with col2:
        target_variable = st.text_input(
            "Target Variable",
            value="CO(GT)",
            key="model_target_variable",
        )

        framework = st.text_input(
            "Framework",
            value="scikit-learn",
            key="model_framework",
        )

        artifact_path = st.text_input(
            "Artifact Path",
            value="models/v2/co_calibration_model.joblib",
            key="model_artifact_path",
        )

    if st.button(
        "Register Model",
        type="primary",
        key="register_model",
    ):
        if not model_name.strip():
            st.warning("Model name is required.")
            return

        if not model_version.strip():
            st.warning("Model version is required.")
            return

        if not artifact_path.strip():
            st.warning("Artifact path is required.")
            return

        try:
            result = api_post(
                "/models/register",
                {
                    "model_name": model_name,
                    "model_version": model_version,
                    "instrument_type": instrument_type,
                    "target_variable": target_variable,
                    "framework": framework,
                    "artifact_path": artifact_path,
                },
            )

            st.success(
                f'Model "{result["model_name"]}" registered successfully.'
            )

            st.json(result)

        except Exception as exc:
            show_api_error(exc)

    st.divider()

    # ========================================================
    # REGISTERED MODELS
    # ========================================================

    try:
        all_models = api_get(
            "/models"
        )

        approved_models = api_get(
            "/models/approved"
        )

        st.subheader("Registered Models")

        models = all_models.get(
            "models",
            [],
        )

        if models:
            st.dataframe(
                models,
                width="stretch",
            )
        else:
            st.info(
                "No models registered."
            )

        # ====================================================
        # APPROVE MODEL
        # ====================================================

        st.divider()

        st.subheader("Model Approval")

        registered_models = [
            model
            for model in models
            if model.get("status") != "approved"
        ]

        if registered_models:

            model_options = {
                (
                    f'{model["model_id"]} — '
                    f'{model["model_name"]} '
                    f'v{model["model_version"]}'
                ): model["model_id"]
                for model in registered_models
            }

            selected_model = st.selectbox(
                "Select model to approve",
                list(model_options.keys()),
                key="approval_model_selector",
            )

            selected_model_id = model_options[
                selected_model
            ]

            if st.button(
                "Approve Selected Model",
                type="primary",
                key="approve_model",
            ):
                try:
                    result = api_post(
                        f"/models/{selected_model_id}/approve"
                    )

                    st.success(
                        f'Model "{result["model_name"]}" approved.'
                    )

                    st.json(result)

                except Exception as exc:
                    show_api_error(exc)

        else:
            st.info(
                "There are no registered models waiting for approval."
            )

        # ====================================================
        # APPROVED MODELS
        # ====================================================

        st.divider()

        st.subheader("Approved Models")

        approved = approved_models.get(
            "models",
            [],
        )

        if approved:
            st.dataframe(
                approved,
                width="stretch",
            )
        else:
            st.info(
                "No approved models."
            )

    except Exception as exc:
        show_api_error(exc)

# ============================================================
# HARDWARE
# ============================================================

def hardware_page():
    st.header("🔌 Hardware")

    try:

        data = api_get(
            "/hardware/drivers"
        )

        st.subheader(
            "Available Drivers"
        )

        for driver in data["drivers"]:

            st.success(
                driver.upper()
            )

        st.divider()

        st.subheader(
            "Hardware Architecture"
        )

        st.write(
            {
                "Simulated": "Software test instrument",
                "Serial": "Serial/COM instrument interface",
                "USB": "USB instrument interface",
                "TCP": "Network instrument interface",
            }
        )

        st.info(
            "Physical serial/USB/TCP operation "
            "requires a compatible real instrument. "
            "The simulator is used for software-only "
            "validation."
        )

    except Exception as exc:
        show_api_error(exc)



# ============================================================
# ANALYTICS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "results"


def analytics_sensor_drift_page():
    st.header("📈 Sensor Drift")
    st.caption(
        "V1 temporal sensor-drift analysis"
    )

    drift_file = RESULTS_DIR / "drift_measurements.csv"
    trends_file = RESULTS_DIR / "drift_trends.csv"

    if not drift_file.exists():
        st.warning(
            "V1 drift measurement results were not found."
        )
        return

    try:
        drift_df = pd.read_csv(drift_file)

        st.subheader("Drift Measurements")

        st.dataframe(
            drift_df,
            width="stretch",
        )

        st.divider()

        if trends_file.exists():

            trends_df = pd.read_csv(
                trends_file
            )

            st.subheader("Drift Trends")

            st.dataframe(
                trends_df,
                width="stretch",
            )

            numeric_columns = trends_df.select_dtypes(
                include="number"
            ).columns.tolist()

            if len(numeric_columns) >= 2:

                x_column = numeric_columns[0]
                y_column = st.selectbox(
                    "Drift Metric",
                    numeric_columns[1:],
                )

                chart_df = trends_df[
                    [x_column, y_column]
                ].dropna()

                if not chart_df.empty:

                    st.line_chart(
                        chart_df.set_index(
                            x_column
                        )
                    )

    except Exception as exc:

        st.error(
            f"Unable to load drift analysis: {exc}"
        )


def analytics_model_performance_page():
    st.header("📊 Model Performance")
    st.caption(
        "V1/V2 calibration-model evaluation"
    )

    performance_file = (
        RESULTS_DIR / "batch_performance.csv"
    )

    comparison_file = (
        RESULTS_DIR / "model_comparison.csv"
    )

    if performance_file.exists():

        try:

            performance_df = pd.read_csv(
                performance_file
            )

            st.subheader(
                "Performance Across Batches"
            )

            st.dataframe(
                performance_df,
                width="stretch",
            )

            numeric_columns = (
                performance_df
                .select_dtypes(include="number")
                .columns
                .tolist()
            )

            if len(numeric_columns) >= 2:

                metric = st.selectbox(
                    "Performance Metric",
                    numeric_columns[1:]
                    if len(numeric_columns) > 1
                    else numeric_columns,
                )

                chart_df = performance_df[
                    [numeric_columns[0], metric]
                ].dropna()

                if not chart_df.empty:

                    st.line_chart(
                        chart_df.set_index(
                            numeric_columns[0]
                        )
                    )

        except Exception as exc:

            st.error(
                f"Unable to load batch performance: {exc}"
            )

    else:

        st.warning(
            "Batch performance results not found."
        )

    st.divider()

    if comparison_file.exists():

        try:

            comparison_df = pd.read_csv(
                comparison_file
            )

            st.subheader(
                "Model Comparison"
            )

            st.dataframe(
                comparison_df,
                width="stretch",
            )

        except Exception as exc:

            st.error(
                f"Unable to load model comparison: {exc}"
            )


def analytics_compensation_page():
    st.header("🧪 Compensation Experiment")
    st.caption(
        "V1 baseline versus drift-corrected experiment"
    )

    comparison_file = (
        RESULTS_DIR /
        "feature_corrected_performance.csv"
    )

    image_file = (
        RESULTS_DIR /
        "baseline_vs_corrected.png"
    )

    if comparison_file.exists():

        try:

            df = pd.read_csv(
                comparison_file
            )

            st.subheader(
                "Baseline vs Corrected"
            )

            st.dataframe(
                df,
                width="stretch",
            )

        except Exception as exc:

            st.error(
                f"Unable to load compensation results: {exc}"
            )

    else:

        st.warning(
            "Compensation experiment results not found."
        )

    if image_file.exists():

        st.subheader(
            "Experiment Visualization"
        )

        st.image(
            str(image_file),
            width="stretch",
        )

    st.info(
        "Interpretation: this experiment is a "
        "research analysis of drift compensation. "
        "It should not be treated as proof of "
        "physical calibration accuracy."
    )


def analytics_page():

    st.header("🧠 Analytics")

    analytics_tab = st.tabs(
        [
            "Sensor Drift",
            "Model Performance",
            "Compensation Experiment",
        ]
    )

    with analytics_tab[0]:
        analytics_sensor_drift_page()

    with analytics_tab[1]:
        analytics_model_performance_page()

    with analytics_tab[2]:
        analytics_compensation_page()


# ============================================================
# MAIN
# ============================================================

def main():
    if not st.session_state.get(
        "authenticated",
        False,
    ):
        login_page()
        return

    st.title(
        "🔬 Lab Calibration System"
    )

    st.caption(
        "Unified V1–V6 Calibration Platform"
    )

    try:

        health = api_get(
            "/health"
        )

        if health.get("status") == "healthy":

            st.sidebar.success(
                "API Online"
            )

        else:

            st.sidebar.error(
                "API Offline"
            )

    except Exception:

        st.sidebar.error(
            "API Offline"
        )

    st.sidebar.title(
        "Navigation"
    )

    page = st.sidebar.radio(
        "Select page",
        [
            "Dashboard",
            "Instruments",
            "Calibration",
            "History",
            "Summary",
            "Analytics",
            "Models",
            "Users",
            "Hardware",
        ],
    )

    if page == "Dashboard":
        dashboard_page()

    elif page == "Instruments":
        instruments_page()

    elif page == "Calibration":
        calibration_page()

    elif page == "History":
        history_page()

    elif page == "Summary":
        summary_page()
    
    elif page == "Analytics":
        analytics_page()

    elif page == "History":
        history_page()

    elif page == "Models":
        models_page()
    
    elif page == "Users":
        users_page()

    elif page == "Hardware":
        hardware_page()


if __name__ == "__main__":
    main()