import joblib
from pathlib import Path

import pandas as pd
import streamlit as st

from src.v3.calibration_report import generate_calibration_report
from src.v3.database import SessionLocal
from src.v3.models import Instrument, CalibrationRecord
from src.v3.calibration_service import save_calibration


# ==================================================
# CONFIGURATION
# ==================================================

MODEL_VERSION = "v2.0.0"

MODEL_PATH = Path(
    "models/v2/co_calibration_model.joblib"
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Lab Calibration System V3",
    page_icon="🔬",
    layout="wide"
)


# ==================================================
# MODEL
# ==================================================

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


model = load_model()


# ==================================================
# DATABASE FUNCTIONS
# ==================================================

def get_instruments():

    db = SessionLocal()

    try:

        instruments = (
            db.query(Instrument)
            .order_by(Instrument.instrument_id)
            .all()
        )

        return instruments

    finally:

        db.close()


def create_instrument(
    name,
    manufacturer,
    model,
    serial_number,
    instrument_type
):

    db = SessionLocal()

    try:

        existing = (
            db.query(Instrument)
            .filter(
                Instrument.serial_number == serial_number
            )
            .first()
        )

        if existing:

            raise ValueError(
                "An instrument with this serial number already exists."
            )

        instrument = Instrument(
            name=name,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            instrument_type=instrument_type,
            status="active"
        )

        db.add(instrument)

        db.commit()

        db.refresh(instrument)

        return instrument

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


def update_instrument(
    instrument_id,
    name,
    manufacturer,
    model,
    serial_number,
    instrument_type
):

    db = SessionLocal()

    try:

        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id == instrument_id
            )
            .first()
        )

        if not instrument:
            raise ValueError(
                "Instrument not found."
            )

        existing = (
            db.query(Instrument)
            .filter(
                Instrument.serial_number == serial_number,
                Instrument.instrument_id != instrument_id
            )
            .first()
        )

        if existing:
            raise ValueError(
                "Another instrument already uses this serial number."
            )

        instrument.name = name
        instrument.manufacturer = manufacturer
        instrument.model = model
        instrument.serial_number = serial_number
        instrument.instrument_type = instrument_type

        db.commit()

        db.refresh(instrument)

        return instrument

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


def update_instrument_status(
    instrument_id,
    new_status
):

    db = SessionLocal()

    try:

        instrument = (
            db.query(Instrument)
            .filter(
                Instrument.instrument_id == instrument_id
            )
            .first()
        )

        if not instrument:

            raise ValueError(
                "Instrument not found."
            )

        if new_status not in [
            "active",
            "inactive"
        ]:

            raise ValueError(
                "Invalid instrument status."
            )

        instrument.status = new_status

        db.commit()

        db.refresh(instrument)

        return instrument

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


def get_calibration_history(
    instrument_id
):

    db = SessionLocal()

    try:

        records = (
            db.query(CalibrationRecord)
            .filter(
                CalibrationRecord.instrument_id
                == instrument_id
            )
            .order_by(
                CalibrationRecord.measurement_time.desc()
            )
            .all()
        )

        return records

    finally:

        db.close()


def calculate_calibration_statistics(
    instrument_id
):

    records = get_calibration_history(
        instrument_id
    )

    valid_records = [
        record
        for record in records
        if record.reference_value > 0
    ]

    if not valid_records:

        return None

    errors = [
        record.error
        for record in valid_records
    ]

    absolute_errors = [
        abs(error)
        for error in errors
    ]

    mae = (
        sum(absolute_errors)
        / len(absolute_errors)
    )

    average_error = (
        sum(errors)
        / len(errors)
    )

    maximum_absolute_error = max(
        absolute_errors
    )

    pass_count = sum(
        1
        for record in valid_records
        if record.status == "PASS"
    )

    fail_count = sum(
        1
        for record in valid_records
        if record.status == "FAIL"
    )

    total_count = len(valid_records)

    pass_rate = (
        (pass_count / total_count) * 100
        if total_count > 0
        else 0
    )

    latest_record = valid_records[0]

    return {
        "count": total_count,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": pass_rate,
        "mae": mae,
        "average_error": average_error,
        "maximum_absolute_error":
            maximum_absolute_error,
        "latest_error": latest_record.error,
        "latest_status": latest_record.status
    }


# ==================================================
# PAGE TITLE
# ==================================================

st.title(
    "🔬 Lab Calibration System V3"
)

st.caption(
    "Instrument management, calibration records, "
    "model-based CO estimation, and calibration tracking."
)


# ==================================================
# REGISTER NEW INSTRUMENT
# ==================================================

st.subheader(
    "➕ Register New Instrument"
)

with st.expander(
    "Register Instrument"
):

    new_name = st.text_input(
        "Instrument Name",
        placeholder="Example: CO Monitor 02"
    )

    new_manufacturer = st.text_input(
        "Manufacturer",
        placeholder="Example: Test Manufacturer"
    )

    new_model = st.text_input(
        "Model",
        placeholder="Example: CO-X200"
    )

    new_serial_number = st.text_input(
        "Serial Number",
        placeholder="Example: CO-2026-002"
    )

    new_instrument_type = st.text_input(
        "Instrument Type",
        placeholder="Example: CO Sensor"
    )

    if st.button(
        "Register Instrument"
    ):

        if not all([
            new_name,
            new_manufacturer,
            new_model,
            new_serial_number,
            new_instrument_type
        ]):

            st.warning(
                "Please fill in all instrument fields."
            )

        else:

            try:

                new_instrument = create_instrument(

                    name=new_name.strip(),

                    manufacturer=
                        new_manufacturer.strip(),

                    model=new_model.strip(),

                    serial_number=
                        new_serial_number.strip(),

                    instrument_type=
                        new_instrument_type.strip()
                )

                st.success(
                    f"Instrument registered successfully. "
                    f"ID: {new_instrument.instrument_id}"
                )

                st.rerun()

            except ValueError as error:

                st.error(
                    str(error)
                )


# ==================================================
# GET INSTRUMENTS
# ==================================================

instruments = get_instruments()


if not instruments:

    st.warning(
        "No instruments are registered."
    )

    st.stop()


# ==================================================
# INSTRUMENT SELECTION
# ==================================================

st.subheader(
    "Instrument Calibration"
)

instrument_options = {

    f"{instrument.name} — "
    f"{instrument.serial_number}":
        instrument

    for instrument in instruments
}


selected_name = st.selectbox(
    "Select Instrument",
    list(instrument_options.keys())
)


selected_instrument = (
    instrument_options[selected_name]
)


st.success(
    f"Selected: {selected_instrument.name} "
    f"(ID: {selected_instrument.instrument_id})"
)


# ==================================================
# INSTRUMENT STATUS
# ==================================================

st.subheader(
    "⚙️ Instrument Status"
)

st.write(
    f"Current Status: "
    f"**{selected_instrument.status}**"
)


if selected_instrument.status == "active":

    if st.button(
        "Deactivate Instrument"
    ):

        try:

            update_instrument_status(

                selected_instrument.instrument_id,

                "inactive"
            )

            st.success(
                "Instrument deactivated successfully."
            )

            st.rerun()

        except ValueError as error:

            st.error(
                str(error)
            )

else:

    if st.button(
        "Activate Instrument"
    ):

        try:

            update_instrument_status(

                selected_instrument.instrument_id,

                "active"
            )

            st.success(
                "Instrument activated successfully."
            )

            st.rerun()

        except ValueError as error:

            st.error(
                str(error)
            )


# ==================================================
# EDIT INSTRUMENT
# ==================================================

# ==================================================
# EDIT INSTRUMENT
# ==================================================

st.subheader(
    "✏️ Edit Instrument"
)

with st.expander(
    "Edit Instrument Details"
):

    with st.form(
        "edit_instrument_form"
    ):

        edit_name = st.text_input(
            "Instrument Name",
            value=selected_instrument.name
        )

        edit_manufacturer = st.text_input(
            "Manufacturer",
            value=selected_instrument.manufacturer
        )

        edit_model = st.text_input(
            "Model",
            value=selected_instrument.model
        )

        edit_serial_number = st.text_input(
            "Serial Number",
            value=selected_instrument.serial_number
        )

        edit_instrument_type = st.text_input(
            "Instrument Type",
            value=selected_instrument.instrument_type
        )

        save_changes = st.form_submit_button(
            "Save Instrument Changes"
        )


    if save_changes:

        if not all([
            edit_name.strip(),
            edit_manufacturer.strip(),
            edit_model.strip(),
            edit_serial_number.strip(),
            edit_instrument_type.strip()
        ]):

            st.warning(
                "Please fill in all instrument fields."
            )

        else:

            try:

                updated_instrument = update_instrument(

                    instrument_id=
                        selected_instrument.instrument_id,

                    name=
                        edit_name.strip(),

                    manufacturer=
                        edit_manufacturer.strip(),

                    model=
                        edit_model.strip(),

                    serial_number=
                        edit_serial_number.strip(),

                    instrument_type=
                        edit_instrument_type.strip()
                )

                st.success(
                    "Instrument updated successfully."
                )

                st.rerun()

            except ValueError as error:

                st.error(
                    str(error)
                )
# ==================================================
# INSTRUMENT INFORMATION
# ==================================================

st.subheader(
    "Instrument Information"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.write(
        f"**Manufacturer:** "
        f"{selected_instrument.manufacturer}"
    )

with col2:

    st.write(
        f"**Model:** "
        f"{selected_instrument.model}"
    )

with col3:

    st.write(
        f"**Serial Number:** "
        f"{selected_instrument.serial_number}"
    )


# ==================================================
# SENSOR MEASUREMENTS
# ==================================================

st.subheader(
    "Sensor Measurements"
)

col1, col2 = st.columns(2)

with col1:

    pt08_s1 = st.number_input(
        "PT08.S1(CO)",
        value=1360.0
    )

    pt08_s2 = st.number_input(
        "PT08.S2(NMHC)",
        value=1046.0
    )

    pt08_s3 = st.number_input(
        "PT08.S3(NOx)",
        value=1056.0
    )

    pt08_s4 = st.number_input(
        "PT08.S4(NO2)",
        value=1692.0
    )


with col2:

    pt08_s5 = st.number_input(
        "PT08.S5(O3)",
        value=1268.0
    )

    temperature = st.number_input(
        "Temperature (°C)",
        value=13.6
    )

    humidity = st.number_input(
        "Relative Humidity (%)",
        value=48.9
    )

    absolute_humidity = st.number_input(
        "Absolute Humidity",
        value=0.7578
    )


# ==================================================
# CALIBRATION INPUTS
# ==================================================

st.subheader(
    "Calibration"
)

reference_co = st.number_input(
    "Reference CO value",
    min_value=0.0,
    value=3.10,
    step=0.01
)

tolerance = st.number_input(
    "Calibration Tolerance",
    min_value=0.0,
    value=0.10,
    step=0.01
)


# ==================================================
# CALIBRATION
# ==================================================

if st.button(
    "🔬 Calibrate",
    type="primary",
    width="stretch"
):

    input_data = pd.DataFrame(

        [[

            pt08_s1,
            pt08_s2,
            pt08_s3,
            pt08_s4,
            pt08_s5,
            temperature,
            humidity,
            absolute_humidity

        ]],

        columns=[

            "PT08.S1(CO)",
            "PT08.S2(NMHC)",
            "PT08.S3(NOx)",
            "PT08.S4(NO2)",
            "PT08.S5(O3)",
            "T",
            "RH",
            "AH"
        ]
    )


    raw_prediction = float(
        model.predict(input_data)[0]
    )


    prediction = max(
        0.0,
        raw_prediction
    )


    try:

        calibration_record = save_calibration(

            instrument_id=
                selected_instrument.instrument_id,

            model_version=
                MODEL_VERSION,

            estimated_value=
                prediction,

            reference_value=
                reference_co,

            tolerance=
                tolerance
        )


        error = (
            calibration_record.error
        )


        absolute_error = abs(
            error
        )


        calibration_status = (
            calibration_record.status
        )


        # ------------------------------------------
        # SESSION STATE
        # ------------------------------------------

        st.session_state[
            "last_prediction"
        ] = prediction

        st.session_state[
            "raw_prediction"
        ] = raw_prediction

        st.session_state[
            "calibration_record_id"
        ] = calibration_record.record_id

        st.session_state[
            "calibration_status"
        ] = calibration_status

        st.session_state[
            "calibration_error"
        ] = error

        st.session_state[
            "calibration_tolerance"
        ] = tolerance

        st.success(
            "Calibration record saved successfully."
        )


    except ValueError as error:

        st.error(
            f"Calibration failed: {error}"
        )


# ==================================================
# CALIBRATION RESULT
# ==================================================

if "last_prediction" in st.session_state:

    prediction = st.session_state[
        "last_prediction"
    ]

    raw_prediction = st.session_state[
        "raw_prediction"
    ]

    record_id = st.session_state[
        "calibration_record_id"
    ]

    calibration_status = (
        st.session_state.get(
            "calibration_status"
        )
    )

    calibration_error = (
        st.session_state.get(
            "calibration_error"
        )
    )

    calibration_tolerance = (
        st.session_state.get(
            "calibration_tolerance"
        )
    )


    st.divider()

    st.subheader(
        "Calibration Result"
    )


    result_col1, result_col2 = (
        st.columns(2)
    )


    with result_col1:

        st.metric(
            "Estimated CO",
            f"{prediction:.2f}"
        )


    with result_col2:

        st.metric(
            "Model Version",
            MODEL_VERSION
        )


    if raw_prediction < 0:

        st.warning(

            f"Raw model prediction was "
            f"{raw_prediction:.4f}. "
            f"The displayed value was constrained "
            f"to a non-negative value."
        )


    # ------------------------------------------
    # PASS / FAIL DISPLAY
    # ------------------------------------------

    if calibration_status == "PASS":

        st.success(

            f"🟢 CALIBRATION PASS — "
            f"Error: {calibration_error:+.4f} "
            f"(Tolerance: "
            f"±{calibration_tolerance:.4f})"
        )


    elif calibration_status == "FAIL":

        st.error(

            f"🔴 CALIBRATION FAIL — "
            f"Error: {calibration_error:+.4f} "
            f"(Tolerance: "
            f"±{calibration_tolerance:.4f})"
        )


    st.write(
        f"**Database Record ID:** "
        f"{record_id}"
    )


    st.info(
        "Prediction generated using the V2 "
        "CO calibration model."
    )


# ==================================================
# CALIBRATION DASHBOARD
# ==================================================

st.divider()

st.subheader(
    "📊 Calibration Dashboard"
)


statistics = (
    calculate_calibration_statistics(
        selected_instrument.instrument_id
    )
)


if statistics is None:

    st.info(
        "No valid calibration records available."
    )

else:

    # ------------------------------------------
    # PRIMARY METRICS
    # ------------------------------------------

    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Total Calibrations",
            statistics["count"]
        )


    with col2:

        st.metric(
            "PASS",
            statistics["pass_count"]
        )


    with col3:

        st.metric(
            "FAIL",
            statistics["fail_count"]
        )


    with col4:

        st.metric(
            "Pass Rate",
            f'{statistics["pass_rate"]:.1f}%'
        )


    # ------------------------------------------
    # ERROR METRICS
    # ------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Mean Absolute Error",
            f'{statistics["mae"]:.4f}'
        )


    with col2:

        st.metric(
            "Average Error",
            f'{statistics["average_error"]:+.4f}'
        )


    with col3:

        st.metric(
            "Maximum Absolute Error",
            f'{statistics["maximum_absolute_error"]:.4f}'
        )


    # ------------------------------------------
    # LATEST STATUS
    # ------------------------------------------

    latest_status = (
        statistics["latest_status"]
    )

    if latest_status == "PASS":

        st.success(

            f'🟢 Latest Calibration: PASS | '
            f'Error: {statistics["latest_error"]:+.4f}'
        )

    else:

        st.error(

            f'🔴 Latest Calibration: FAIL | '
            f'Error: {statistics["latest_error"]:+.4f}'
        )


# ==================================================
# CALIBRATION TREND
# ==================================================

st.subheader(
    "📈 Calibration Trend"
)


history = get_calibration_history(
    selected_instrument.instrument_id
)


if history:

    trend_data = []


    for record in reversed(history):

        if record.reference_value > 0:

            trend_data.append({

                "Date/Time":
                    record.measurement_time,

                "Estimated CO":
                    record.estimated_value,

                "Reference CO":
                    record.reference_value,

                "Error":
                    record.error
            })


    if trend_data:

        trend_df = pd.DataFrame(
            trend_data
        )


        st.write(
            "Estimated CO vs Reference CO"
        )


        comparison_df = (
            trend_df
            .set_index("Date/Time")
            [
                [
                    "Estimated CO",
                    "Reference CO"
                ]
            ]
        )


        st.line_chart(
            comparison_df,
            width="stretch"
        )


        st.write(
            "Calibration Error"
        )


        error_df = (
            trend_df
            .set_index("Date/Time")
            [
                ["Error"]
            ]
        )


        st.line_chart(
            error_df,
            width="stretch"
        )


    else:

        st.info(
            "No valid calibration data "
            "available for charts."
        )


else:

    st.info(
        "No calibration records available."
    )


# ==================================================
# CALIBRATION HISTORY
# ==================================================

st.subheader(
    "📋 Calibration History"
)


if not history:

    st.info(
        "No calibration records found "
        "for this instrument."
    )

else:

    history_data = []


    for record in history:

        history_data.append({

            "Record ID":
                record.record_id,

            "Date/Time":
                record.measurement_time,

            "Model":
                record.model_version,

            "Estimated CO":
                round(
                    record.estimated_value,
                    4
                ),

            "Reference CO":
                round(
                    record.reference_value,
                    4
                ),

            "Error":
                round(
                    record.error,
                    4
                ),

            "Tolerance":
                round(
                    record.tolerance,
                    4
                ),

            "Status":
                record.status
        })


    history_df = pd.DataFrame(
        history_data
    )


    st.dataframe(

        history_df,

        width="stretch",

        hide_index=True
    )
    # ==================================================
# CALIBRATION REPORT
# ==================================================

st.divider()

st.subheader(
    "📄 Calibration Report"
)

report_records = get_calibration_history(
    selected_instrument.instrument_id
)

if report_records:

    latest_record = report_records[0]

    statistics = calculate_calibration_statistics(
        selected_instrument.instrument_id
    )

    report_pdf = generate_calibration_report(
        instrument=selected_instrument,
        record=latest_record,
        statistics=statistics
    )

    filename = (
        f"calibration_report_"
        f"{selected_instrument.serial_number}_"
        f"record_{latest_record.record_id}.pdf"
    )

    st.download_button(
        label="📥 Download Latest Calibration Report",
        data=report_pdf,
        file_name=filename,
        mime="application/pdf",
        width="stretch"
    )

else:

    st.info(
        "Create a calibration record before generating a report."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    f"Lab Calibration System V3 | "
    f"Model {MODEL_VERSION} | "
    f"SQLite database"
)