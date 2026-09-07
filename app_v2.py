import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_FILE = "models/v2/co_calibration_model.pkl"

VALIDATION_MAE = 0.3693
VALIDATION_RMSE = 0.5577
VALIDATION_R2 = 0.8311

CO_MIN = 0.1
CO_MAX = 11.9


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="V2 CO Sensor Calibration",
    page_icon="🔬",
    layout="wide"
)


# ============================================================
# LOAD MODEL
# ============================================================

if not os.path.exists(MODEL_FILE):

    st.error(
        "Calibration model was not found. "
        "Please train the V2 model first."
    )

    st.stop()


model_data = joblib.load(MODEL_FILE)

model = model_data["model"]
features = model_data["features"]
target = model_data["target"]


# ============================================================
# HEADER
# ============================================================

st.title("🔬 V2 — CO Sensor Calibration")

st.write(
    "A machine-learning calibration prototype that converts "
    "multi-sensor measurements into an estimated CO concentration."
)

st.info(
    "This is a research/learning calibration prototype. "
    "The prediction is an estimate and should not be treated "
    "as a certified laboratory measurement."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("V2 Calibration System")

st.sidebar.markdown(
    """
### System

**Model:** Linear Regression

**Target:** CO(GT)

**Input Features:** 8

**Validation R²:** 0.8311

**Validation MAE:** 0.3693
"""
)

st.sidebar.divider()

st.sidebar.write(
    "CO reference range used during model development:"
)

st.sidebar.write(
    f"**{CO_MIN:.1f} – {CO_MAX:.1f}**"
)


# ============================================================
# SENSOR INPUT SECTION
# ============================================================

st.header("📡 Sensor Measurements")

st.write(
    "Enter the measurements produced by the sensor system."
)

col1, col2 = st.columns(2)


with col1:

    s1 = st.number_input(
        "PT08.S1(CO)",
        min_value=0.0,
        value=1360.0,
        step=1.0
    )

    s2 = st.number_input(
        "PT08.S2(NMHC)",
        min_value=0.0,
        value=1046.0,
        step=1.0
    )

    s3 = st.number_input(
        "PT08.S3(NOx)",
        min_value=0.0,
        value=1056.0,
        step=1.0
    )

    s4 = st.number_input(
        "PT08.S4(NO2)",
        min_value=0.0,
        value=1692.0,
        step=1.0
    )


with col2:

    s5 = st.number_input(
        "PT08.S5(O3)",
        min_value=0.0,
        value=1268.0,
        step=1.0
    )

    temperature = st.number_input(
        "Temperature (°C)",
        value=13.6,
        step=0.1
    )

    humidity = st.number_input(
        "Relative Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=48.9,
        step=0.1
    )

    absolute_humidity = st.number_input(
        "Absolute Humidity",
        min_value=0.0,
        value=0.7578,
        step=0.0001,
        format="%.4f"
    )


# ============================================================
# CALIBRATION BUTTON
# ============================================================

st.divider()

calibrate = st.button(
    "🔬 Calibrate CO",
    type="primary",
    use_container_width=True
)


# ============================================================
# CALIBRATION
# ============================================================

if calibrate:

    # Create input DataFrame
    input_data = pd.DataFrame(
        [{
            "PT08.S1(CO)": s1,
            "PT08.S2(NMHC)": s2,
            "PT08.S3(NOx)": s3,
            "PT08.S4(NO2)": s4,
            "PT08.S5(O3)": s5,
            "T": temperature,
            "RH": humidity,
            "AH": absolute_humidity
        }]
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    raw_prediction = model.predict(input_data)[0]

    # Physical constraint
    prediction = max(0.0, raw_prediction)


    # ========================================================
    # RESULT
    # ========================================================

    st.header("📊 Calibration Result")

    result_col1, result_col2 = st.columns(2)


    with result_col1:

        st.metric(
            "Estimated CO Concentration",
            f"{prediction:.2f}"
        )


    with result_col2:

        if raw_prediction < 0:

            st.warning(
                "The raw model prediction was below zero. "
                "The displayed value was constrained to zero."
            )

        else:

            st.success(
                "Prediction is physically non-negative."
            )


    # ========================================================
    # QUALITY INFORMATION
    # ========================================================

    st.subheader("📈 Model Validation")

    metric1, metric2, metric3 = st.columns(3)


    with metric1:

        st.metric(
            "MAE",
            f"{VALIDATION_MAE:.4f}"
        )


    with metric2:

        st.metric(
            "RMSE",
            f"{VALIDATION_RMSE:.4f}"
        )


    with metric3:

        st.metric(
            "R²",
            f"{VALIDATION_R2:.4f}"
        )


    st.caption(
        "These metrics come from the chronological validation experiment. "
        "They describe overall model performance and do not guarantee "
        "the accuracy of this individual prediction."
    )


    # ========================================================
    # RANGE CHECK
    # ========================================================

    st.subheader("🎯 Reference Range Check")

    if CO_MIN <= prediction <= CO_MAX:

        st.success(
            f"The prediction ({prediction:.2f}) is within the "
            f"CO range observed during model development "
            f"({CO_MIN:.1f}–{CO_MAX:.1f})."
        )

    elif prediction < CO_MIN:

        st.warning(
            f"The prediction ({prediction:.2f}) is below the "
            f"lowest CO reference value observed during model development "
            f"({CO_MIN:.1f})."
        )

    else:

        st.warning(
            f"The prediction ({prediction:.2f}) is above the "
            f"highest CO reference value observed during model development "
            f"({CO_MAX:.1f})."
        )


    # ========================================================
    # INPUT SUMMARY
    # ========================================================

    st.subheader("🔎 Measurement Summary")

    display_data = pd.DataFrame(
        {
            "Measurement": [
                "PT08.S1(CO)",
                "PT08.S2(NMHC)",
                "PT08.S3(NOx)",
                "PT08.S4(NO2)",
                "PT08.S5(O3)",
                "Temperature (°C)",
                "Relative Humidity (%)",
                "Absolute Humidity"
            ],

            "Value": [
                s1,
                s2,
                s3,
                s4,
                s5,
                temperature,
                humidity,
                absolute_humidity
            ]
        }
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # CALIBRATION RECORD
    # ========================================================

    st.subheader("🧾 Calibration Record")

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    record = pd.DataFrame(
        [{
            "Timestamp": timestamp,
            "PT08.S1(CO)": s1,
            "PT08.S2(NMHC)": s2,
            "PT08.S3(NOx)": s3,
            "PT08.S4(NO2)": s4,
            "PT08.S5(O3)": s5,
            "Temperature": temperature,
            "RH": humidity,
            "AH": absolute_humidity,
            "Predicted_CO": prediction
        }]
    )

    st.dataframe(
        record,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # DOWNLOAD RESULT
    # ========================================================

    csv_data = record.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Calibration Result",
        data=csv_data,
        file_name="co_calibration_result.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "V2 CO Sensor Calibration Prototype | "
    "Linear Regression | Research/Educational Use"
)