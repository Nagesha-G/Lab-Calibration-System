import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sensor Calibration & Drift Monitor",
    page_icon="🔬",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

DATA_FILE = "data/processed/sensor_data_with_batch.csv"
DRIFT_FILE = "results/drift_measurements.csv"
PERFORMANCE_FILE = "results/batch_performance.csv"
COMPARISON_FILE = "results/model_comparison.csv"


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_FILE)

    return df


@st.cache_data
def load_drift():

    return pd.read_csv(DRIFT_FILE)


@st.cache_data
def load_performance():

    return pd.read_csv(PERFORMANCE_FILE)


@st.cache_data
def load_comparison():

    return pd.read_csv(COMPARISON_FILE)


df = load_data()
drift_df = load_drift()
performance_df = load_performance()
comparison_df = load_comparison()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔬 Navigation")

page = st.sidebar.radio(
    "Select view",
    [
        "Dashboard",
        "Sensor Drift",
        "Model Performance",
        "Compensation Experiment",
        "Data Explorer"
    ]
)


st.sidebar.markdown("---")

st.sidebar.info(
    """
    **V1 Prototype**

    This application analyzes sensor
    drift and evaluates machine-learning
    performance across time-separated
    sensor batches.
    """
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.title("🔬 Sensor Calibration & Drift Monitor")

    st.subheader(
        "V1 — Sensor Drift Analysis Prototype"
    )

    st.markdown(
        """
        This system analyzes sensor measurements collected
        across multiple batches and determines whether
        sensor behavior changes over time.
        """
    )

    st.markdown("---")

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Measurements",
            f"{len(df):,}"
        )

    with col2:
        st.metric(
            "Sensor Features",
            "128"
        )

    with col3:
        st.metric(
            "Batches",
            df["batch"].nunique()
        )

    with col4:
        st.metric(
            "Gas Classes",
            df["label"].nunique()
        )

    st.markdown("---")

    # --------------------------------------------------------
    # MODEL SUMMARY
    # --------------------------------------------------------

    st.header("🧠 Model Summary")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Random-Split Accuracy",
            "98.99%"
        )

        st.caption(
            "Useful as a general classification baseline."
        )

    with col2:

        latest_accuracy = performance_df.iloc[-1]["accuracy"]

        st.metric(
            "Latest Future-Batch Accuracy",
            f"{latest_accuracy * 100:.2f}%"
        )

        st.caption(
            "Model trained on batches 1–7 and evaluated on batch 10."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # OVERALL DIAGNOSIS
    # --------------------------------------------------------

    st.header("⚠ System Diagnosis")

    latest_accuracy = performance_df.iloc[-1]["accuracy"]

    if latest_accuracy < 0.80:

        st.error(
            f"""
            **Sensor drift / temporal distribution shift detected.**

            Model accuracy on the latest unseen batch is
            **{latest_accuracy * 100:.2f}%**, compared with the
            original random-split baseline of **98.99%**.

            The model does not generalize equally well to
            later batches.
            """
        )

    else:

        st.success(
            "Model performance remains relatively stable."
        )

    st.markdown("---")

    st.info(
        """
        **Important:** This V1 system demonstrates sensor
        drift and model degradation. It is not yet a physical
        calibration system because the current dataset does
        not provide a direct physical reference value for
        calibration regression.
        """
    )


# ============================================================
# SENSOR DRIFT
# ============================================================

elif page == "Sensor Drift":

    st.title("📊 Sensor Drift Analysis")

    st.write(
        """
        Sensor measurements can change as the sensor system
        moves through different batches and operating periods.
        """
    )

    # --------------------------------------------------------
    # BATCH MEANS
    # --------------------------------------------------------

    st.subheader("Average Sensor Response by Batch")

    selected_features = st.multiselect(
        "Select sensor features",
        [
            "feature_1",
            "feature_2",
            "feature_3",
            "feature_17",
            "feature_33"
        ],
        default=[
            "feature_1",
            "feature_2"
        ]
    )

    if selected_features:

        batch_means = (
            df.groupby("batch")[selected_features]
            .mean()
        )

        st.line_chart(batch_means)

    # --------------------------------------------------------
    # DRIFT TABLE
    # --------------------------------------------------------

    st.subheader("Measured Drift")

    st.dataframe(
        drift_df.sort_values(
            "percent_change",
            key=lambda x: x.abs(),
            ascending=False
        ),
        use_container_width=True
    )

    st.caption(
        "Percentage change compares batch 1 with batch 10 "
        "for the same gas class."
    )


# ============================================================
# MODEL PERFORMANCE
# ============================================================

elif page == "Model Performance":

    st.title("🧠 Model Performance")

    st.write(
        """
        The model is trained on earlier batches and tested
        on later batches. This simulates deployment on future
        sensor conditions.
        """
    )

    # --------------------------------------------------------
    # PERFORMANCE GRAPH
    # --------------------------------------------------------

    st.subheader(
        "Performance on Future Batches"
    )

    chart_data = performance_df.set_index(
        "batch"
    )["accuracy"]

    st.line_chart(chart_data)

    # --------------------------------------------------------
    # PERFORMANCE TABLE
    # --------------------------------------------------------

    st.subheader("Batch Results")

    display_df = performance_df.copy()

    display_df["accuracy"] = (
        display_df["accuracy"] * 100
    ).round(2)

    display_df = display_df.rename(
        columns={
            "accuracy": "Accuracy (%)"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True
    )

    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------

    st.subheader("What does this mean?")

    st.markdown(
        """
        **Batch 8:** The model still performs well.

        **Batch 9:** Performance decreases substantially.

        **Batch 10:** Performance reaches approximately
        72.5%.

        This indicates that a model trained on earlier sensor
        conditions does not maintain the same performance on
        later batches.
        """
    )


# ============================================================
# COMPENSATION EXPERIMENT
# ============================================================

elif page == "Compensation Experiment":

    st.title("🔧 Drift Compensation Experiment")

    st.write(
        """
        We tested whether feature-wise linear drift correction
        could restore model performance.
        """
    )

    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    display = comparison_df.copy()

    display["baseline_accuracy"] *= 100
    display["corrected_accuracy"] *= 100
    display["improvement"] *= 100

    display = display.rename(
        columns={
            "baseline_accuracy": "Baseline (%)",
            "corrected_accuracy": "Corrected (%)",
            "improvement": "Change (percentage points)"
        }
    )

    st.dataframe(
        display,
        use_container_width=True
    )

    # --------------------------------------------------------
    # GRAPH
    # --------------------------------------------------------

    chart = comparison_df.set_index(
        "batch"
    )[
        [
            "baseline_accuracy",
            "corrected_accuracy"
        ]
    ] * 100

    chart.columns = [
        "Baseline",
        "Drift Corrected"
    ]

    st.line_chart(chart)

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    st.subheader("Experiment Result")

    average_change = (
        comparison_df["improvement"].mean()
        * 100
    )

    if average_change < 0:

        st.error(
            f"""
            ❌ **Correction rejected**

            The feature-wise correction reduced average
            performance by approximately
            **{abs(average_change):.2f} percentage points**.

            Therefore this correction method should not be
            used as the final compensation algorithm.
            """
        )

    else:

        st.success(
            f"""
            The correction improved average performance by
            approximately {average_change:.2f} percentage points.
            """
        )

    st.markdown("---")

    st.info(
        """
        **Engineering decision:**

        Do not deploy this correction method.

        The experiment shows why model validation on future
        batches is necessary before calling a calibration
        algorithm successful.
        """
    )


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    st.title("🔎 Data Explorer")

    st.write(
        "Explore the processed sensor measurements."
    )

    col1, col2 = st.columns(2)

    with col1:

        selected_batch = st.selectbox(
            "Select batch",
            sorted(df["batch"].unique())
        )

    with col2:

        selected_label = st.selectbox(
            "Select gas class",
            sorted(df["label"].unique())
        )

    filtered = df[
        (df["batch"] == selected_batch)
        &
        (df["label"] == selected_label)
    ]

    st.metric(
        "Matching measurements",
        len(filtered)
    )

    st.dataframe(
        filtered.head(100),
        use_container_width=True
    )

    st.caption(
        "Showing the first 100 matching records."
    )