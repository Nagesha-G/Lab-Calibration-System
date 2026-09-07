# 🔬 Lab Calibration System

An end-to-end experimental platform for **sensor drift analysis, calibration modeling, and laboratory instrument management**.

This project is being developed incrementally, starting with data-driven sensor analysis and progressing toward a complete calibration platform for laboratory instruments.

---

## 🚀 Project Vision

Laboratory sensors and instruments can change their behavior over time because of factors such as:

* Sensor aging
* Environmental changes
* Measurement drift
* Temperature and humidity variation
* Instrument degradation
* Changing operating conditions

The long-term goal of this project is to build a software platform that can:

```text
Raw Sensor Measurements
          ↓
Data Quality Analysis
          ↓
Drift Detection
          ↓
Calibration Model
          ↓
Calibrated Measurement
          ↓
Instrument History
          ↓
Automated Calibration
          ↓
Multi-Instrument Platform
```

The project is currently at **V2 — Calibration Prototype**.

---

# 📌 Current Status

| Version | Status     | Description                           |
| ------- | ---------- | ------------------------------------- |
| V1.0.0  | ✅ Complete | Sensor drift analysis                 |
| V2.0.0  | ✅ Complete | CO sensor calibration prototype       |
| V3.0.0  | 🔜 Planned | Database + instrument management      |
| V4.0.0  | 🔜 Planned | API + scheduling                      |
| V5.0.0  | 🔜 Planned | Multi-instrument platform             |
| V6.0.0  | 🔜 Planned | Real hardware + laboratory deployment |

---

# 🧪 V1 — Sensor Drift Analysis

The first version focused on understanding how sensor measurements change across different measurement batches.

### Dataset

**UCI Gas Sensor Array Drift Dataset**

The dataset contains:

* 13,910 measurements
* 128 derived sensor features
* 10 measurement batches
* 6 gas classes

The raw data was parsed and converted into structured CSV files for analysis.

### Data quality

The processed dataset contains:

* No missing values
* No duplicate records
* 13,910 usable measurements

---

## 📈 V1 Baseline Model

A Logistic Regression model with StandardScaler was used as the initial classification baseline.

### Random Stratified Split

```text
Accuracy: 98.99%
```

However, a random split does not properly simulate future sensor measurements.

---

## ⏱️ Time-Based Validation

The model was trained on earlier batches and evaluated on later batches.

| Batch    | Accuracy |
| -------- | -------: |
| Batch 8  |   91.50% |
| Batch 9  |   74.04% |
| Batch 10 |   72.53% |

This experiment demonstrated a major difference between random validation and chronological validation.

```text
Random split
98.99%
     ↓
Future Batch 8
91.50%
     ↓
Future Batch 9
74.04%
     ↓
Future Batch 10
72.53%
```

This indicates significant temporal distribution shift.

Importantly, the project does **not** assume that all of this degradation is necessarily caused by physical sensor drift; future investigation is required to separate sensor effects from other distribution changes.

---

# 🧭 V1 Drift Investigation

Measurements were compared across batches while controlling for gas class.

Several features showed substantial changes between early and late batches.

Examples:

| Feature    | Class |   Change |
| ---------- | ----: | -------: |
| feature_2  |     2 | +128.01% |
| feature_3  |     4 |  −89.89% |
| feature_1  |     4 |  −89.69% |
| feature_33 |     5 |  +83.79% |
| feature_3  |     6 |  −82.34% |
| feature_1  |     6 |  −82.18% |

These results motivated the move from simple drift detection toward calibration modeling.

---

# 🧪 V1 Compensation Experiment

A feature-wise linear drift correction method was tested.

The correction model estimated a trend for each feature across training batches and attempted to remove the estimated trend before classification.

The result was worse than the baseline:

| Batch    | Baseline | Corrected |    Change |
| -------- | -------: | --------: | --------: |
| Batch 8  |   91.50% |    90.48% |  −1.02 pp |
| Batch 9  |   74.04% |    62.13% | −11.91 pp |
| Batch 10 |   72.53% |    62.92% |  −9.61 pp |

The correction method was therefore **rejected rather than forced into the system**.

This is an important part of the experimental process: a proposed correction method should demonstrate measurable improvement before being considered useful.

---

# 🎯 V2 — CO Sensor Calibration Prototype

V2 changes the problem from classification toward **continuous calibration**.

Instead of predicting a gas class, the system estimates a reference CO concentration from sensor measurements.

### Dataset

**UCI Air Quality Dataset**

The dataset contains measurements from an air-quality monitoring system in an Italian city.

For V2, the relevant measurements were cleaned and transformed into a calibration dataset.

### Data cleaning

The dataset uses `-200` as a missing-value marker.

These values were converted to missing values and rows lacking required measurements were removed.

```text
Original rows: 9471

Clean rows:    7344
```

The resulting calibration dataset contains:

```text
7344 measurements
8 input variables
1 calibration target
```

---

# 🔧 V2 Calibration Inputs

The model uses eight measurements:

```text
PT08.S1(CO)
PT08.S2(NMHC)
PT08.S3(NOx)
PT08.S4(NO2)
PT08.S5(O3)
Temperature
Relative Humidity
Absolute Humidity
```

### Target

```text
CO(GT)
```

The objective is:

```text
Sensor Measurements
        ↓
Calibration Model
        ↓
Estimated CO Concentration
```

---

# 🤖 V2 Model Experiments

Two regression approaches were evaluated.

### Linear Regression

Chronological validation:

```text
MAE  = 0.3693
RMSE = 0.5577
R²   = 0.8311
```

### Random Forest

```text
MAE  = 0.4094
RMSE = 0.6245
R²   = 0.7882
```

The Linear Regression model performed better on the chronological validation set and was therefore selected as the V2 baseline calibration model.

---

# 🔬 Feature Analysis

Feature contribution was examined using the standardized linear model.

The strongest predictive contributors included:

```text
PT08.S2(NMHC)
PT08.S1(CO)
PT08.S4(NO2)
Temperature
PT08.S3(NOx)
```

These coefficients represent **predictive contributions**, not causal physical relationships.

---

# 📉 Feature Reduction Experiment

The model was tested using different numbers of features.

| Features |    MAE |   RMSE |     R² |
| -------- | -----: | -----: | -----: |
| All 8    | 0.3693 | 0.5577 | 0.8311 |
| Top 5    | 0.3753 | 0.5608 | 0.8292 |
| Top 3    | 0.4231 | 0.6075 | 0.7996 |
| Top 2    | 0.4504 | 0.6136 | 0.7955 |

The full eight-feature model performed best, so all eight inputs are retained for V2.

---

# 🖥️ V2 Streamlit Application

V2 includes an interactive Streamlit calibration application.

The application allows a user to enter sensor measurements and receive an estimated CO concentration.

### Application capabilities

* Sensor measurement input
* CO concentration prediction
* Physical non-negative output constraint
* Validation metrics
* Target-range check
* Measurement summary
* Calibration record
* CSV export

### Application flow

```text
User enters sensor measurements
              ↓
        StandardScaler
              ↓
       Linear Regression
              ↓
        CO prediction
              ↓
     Physical validation
              ↓
       Calibration record
```

---

# 📊 Example V2 Result

Example sensor measurements can be entered through the Streamlit interface.

The application produces:

```text
Estimated CO
Validation MAE
Validation RMSE
Validation R²
Reference range check
Calibration record
```

The current model is an **experimental calibration model**, not a certified laboratory calibration system.

---

# 🗂️ Project Structure

```text
lab-calibration-system/
│
├── app.py
├── app_v2.py
├── README.md
├── .gitignore
│
├── data/
│   ├── processed/
│   │   ├── sensor_data.csv
│   │   └── sensor_data_with_batch.csv
│   │
│   └── v2/
│       ├── air_quality_clean.csv
│       └── co_calibration_dataset.csv
│
├── models/
│   └── v2/
│       └── co_calibration_model.pkl
│
├── notebooks/
│
├── results/
│   ├── drift_measurements.csv
│   ├── batch_performance.csv
│   ├── model_comparison.csv
│   ├── baseline_vs_corrected.png
│   └── model_performance_over_time.png
│
└── src/
    ├── analyze_data.py
    ├── analyze_drift.py
    ├── baseline_model.py
    ├── batch_performance.py
    ├── controlled_drift.py
    ├── drift_compensation.py
    ├── feature_drift_correction.py
    ├── measure_drift.py
    ├── parse_data.py
    ├── visualize_data.py
    │
    └── v2/
        ├── prepare_data.py
        ├── build_calibration_dataset.py
        ├── baseline_calibration.py
        ├── time_calibration_test.py
        ├── analyze_prediction_errors.py
        ├── random_forest_calibration.py
        ├── feature_importance.py
        ├── feature_reduction_test.py
        └── train_final_model.py
```

---

# 🛠️ Technology Stack

### Programming

* Python

### Data Science

* Pandas
* NumPy
* Scikit-learn

### Visualization

* Matplotlib
* Seaborn

### Application

* Streamlit

### Development

* Git
* GitHub
* Jupyter Notebook

---

# ▶️ Running the Project

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/lab-calibration-system.git
cd lab-calibration-system
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter streamlit
```

Run the V1 application:

```bash
streamlit run app.py
```

Run the V2 calibration application:

```bash
streamlit run app_v2.py
```

---

# ⚠️ Current Limitations

This project is still an experimental research/development system.

### V1

The UCI Gas Sensor Array Drift dataset demonstrates sensor-array drift and temporal distribution shift, but its class labels should **not** be interpreted as physical calibration reference values.

### V2

The current CO model demonstrates a data-driven calibration workflow, but it is not yet sufficient for laboratory certification or real-world instrument calibration.

The current system does not yet provide:

* Certified reference standards
* Instrument-specific calibration procedures
* Persistent calibration history
* User authentication
* Database-backed instrument management
* Calibration scheduling
* Model version management
* Automated quality-control workflows
* Hardware communication
* Laboratory deployment

Therefore:

> **The current system is a calibration software prototype, not a certified laboratory calibration system.**

---

# 🧠 Engineering Principle

The project follows an experimental approach:

```text
Hypothesis
    ↓
Measurement
    ↓
Experiment
    ↓
Validation
    ↓
Compare
    ↓
Accept or Reject
```

For example, the V1 drift-correction experiment produced worse future-batch performance.

Instead of presenting the correction as successful, the method was rejected.

This principle will continue throughout the project.

---

# 🗺️ Roadmap

## V1 — Sensor Drift Analysis ✅

* [x] Dataset acquisition
* [x] Data parsing
* [x] Data quality analysis
* [x] Batch analysis
* [x] Drift analysis
* [x] Temporal validation
* [x] Drift compensation experiment
* [x] Streamlit dashboard

## V2 — Calibration Prototype ✅

* [x] Calibration dataset creation
* [x] Missing-value handling
* [x] Regression baseline
* [x] Chronological validation
* [x] Random Forest comparison
* [x] Feature analysis
* [x] Feature reduction experiment
* [x] Final calibration model
* [x] Streamlit calibration application

## V3 — Instrument Management 🔜

Planned capabilities:

* [ ] Database
* [ ] Instrument registration
* [ ] Sensor/instrument IDs
* [ ] Persistent calibration history
* [ ] Calibration records
* [ ] Model version tracking
* [ ] Calibration status
* [ ] Instrument health tracking

## V4 — API + Scheduling 🔜

* [ ] REST API
* [ ] Automated calibration jobs
* [ ] Calibration scheduling
* [ ] Background processing
* [ ] Alerts
* [ ] Audit logs

## V5 — Multi-Instrument Platform 🔜

* [ ] Multiple instrument types
* [ ] Multiple calibration models
* [ ] Instrument-specific models
* [ ] Model registry
* [ ] Cross-instrument analysis

## V6 — Hardware + Laboratory Deployment 🔜

* [ ] Real sensor integration
* [ ] Instrument communication
* [ ] Reference standards
* [ ] Real-time measurement ingestion
* [ ] Hardware-in-the-loop testing
* [ ] Laboratory validation

---

# 📚 Data Sources

### UCI Gas Sensor Array Drift Dataset

Used for V1 sensor drift and temporal distribution-shift experiments.

### UCI Air Quality Dataset

Used for V2 CO calibration modeling.

The datasets remain subject to their respective licenses and usage conditions. The current V1 dataset should not be treated as a commercial calibration dataset.

---

# 🎯 Long-Term Goal

The ultimate objective is to evolve this prototype into a platform capable of managing the complete lifecycle of laboratory instrument calibration:

```text
                 LAB CALIBRATION PLATFORM

        ┌──────────────────────────────┐
        │       Raw Measurements       │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │       Data Validation        │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │      Drift Detection         │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    Calibration Model         │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Calibrated Measurement     │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    Instrument Database       │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │ Scheduling + Automation      │
        └──────────────────────────────┘
```

The project is being developed incrementally, with each version adding another layer toward a production-grade calibration platform.

---

## 👨‍💻 Author

**Nagesh**

Building the project from first principles — from raw sensor data to an end-to-end laboratory calibration platform.
