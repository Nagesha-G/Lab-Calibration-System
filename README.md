````markdown
# 🔬 Lab Calibration System

A software platform for analyzing sensor drift, building sensor-to-reference calibration models, and managing instrument calibration records.

The project is developed incrementally from **sensor data analysis → machine-learning calibration → calibration management software**.

---

## 🚀 Project Evolution

```text
V1
Sensor Drift Analysis
        ↓
V2
Machine Learning Calibration
        ↓
V3
Calibration Management System
        ↓
V4
API + Scheduling
        ↓
V5
Multi-Instrument Platform
        ↓
V6
Real Hardware + Laboratory Deployment
````

---

# 📌 Project Overview

Modern laboratory and industrial instruments can experience measurement changes over time because of sensor aging, environmental conditions, operating conditions, and other sources of distribution shift.

The goal of this project is to build a software system that can:

* Analyze sensor behavior over time
* Detect temporal distribution changes
* Build machine-learning calibration models
* Compare estimated measurements against reference values
* Determine calibration PASS/FAIL status
* Maintain instrument records
* Store calibration history
* Generate calibration reports
* Provide a foundation for future automated calibration workflows

The project currently contains three completed versions.

---

# 🧪 V1 — Sensor Drift Analysis

## Objective

V1 investigates whether sensor measurements change across different data batches and whether a model trained on earlier measurements continues to perform well on later measurements.

The purpose of V1 is **sensor drift analysis and temporal robustness**, not physical calibration.

---

## Dataset

V1 uses the:

**UCI Gas Sensor Array Drift Dataset**

The dataset contains:

* 13,910 measurements
* 128 sensor-derived features
* 10 batches
* 6 gas classes

The raw dataset contains measurements represented using feature-value pairs.

The dataset uses 16 chemical sensors with 128 derived features.

---

## V1 Data Processing

The raw `.dat` files were parsed into a structured CSV dataset.

Output:

```text
data/processed/sensor_data.csv
```

and:

```text
data/processed/sensor_data_with_batch.csv
```

The processed dataset contains:

```text
13,910 rows
128 features
1 class label
1 batch identifier
```

---

# 📊 V1 Drift Analysis

The project compares sensor behavior across batches.

Example measured changes between Batch 1 and Batch 10 include:

| Feature    | Class |   Change |
| ---------- | ----: | -------: |
| feature_2  |     2 | +128.01% |
| feature_3  |     4 |  −89.89% |
| feature_1  |     4 |  −89.69% |
| feature_33 |     5 |  +83.79% |
| feature_3  |     6 |  −82.34% |
| feature_1  |     6 |  −82.18% |

These results demonstrate substantial changes in feature distributions across time.

However, these changes should not automatically be interpreted as purely physical sensor drift because temporal distribution shift can have multiple causes.

---

# 🤖 V1 Baseline Model

A Logistic Regression model was trained using:

```text
StandardScaler
+
LogisticRegression
```

using all 128 features.

### Random Stratified Split

Accuracy:

```text
98.99%
```

This result demonstrates strong performance when training and testing data are randomly sampled from the overall dataset.

However, this validation method does not adequately simulate deployment on future batches.

---

# ⏱️ V1 Time-Based Validation

The model was trained using:

```text
Batches 1–7
```

and evaluated on future batches:

```text
Batch 8
Batch 9
Batch 10
```

Results:

| Batch    | Samples | Accuracy |
| -------- | ------: | -------: |
| Batch 8  |     294 |   91.50% |
| Batch 9  |     470 |   74.04% |
| Batch 10 |   3,600 |   72.53% |

This is one of the key findings of V1.

A random split produced:

```text
98.99%
```

while future-batch performance dropped to:

```text
72.53%
```

This demonstrates that random validation can substantially overestimate performance when the deployment environment contains temporal distribution shift.

---

# 🧮 V1 Drift Compensation Experiment

Several normalization and drift-correction experiments were performed.

A feature-wise linear drift correction model was tested by estimating feature trends across training batches and removing the predicted trend.

The correction was rejected because it reduced future-batch performance.

Example:

| Batch    | Baseline | Corrected |    Change |
| -------- | -------: | --------: | --------: |
| Batch 8  |   91.50% |    90.48% |  −1.02 pp |
| Batch 9  |   74.04% |    62.13% | −11.91 pp |
| Batch 10 |   72.53% |    62.92% |  −9.61 pp |

The important engineering decision was to **reject the correction rather than force an improvement**.

---

# 🖥️ V1 Streamlit Dashboard

V1 includes a Streamlit dashboard with:

* 📊 Dashboard
* 📈 Sensor Drift
* 🤖 Model Performance
* 🧮 Compensation Experiment
* 🔎 Data Explorer

The dashboard provides visual access to the drift analysis and model performance results.

---

# 🧪 V2 — Machine Learning Calibration

## Objective

V2 moves from classification/drift analysis toward an actual calibration problem.

Instead of predicting a gas class, the model predicts a physical measurement from sensor readings.

The target selected for V2 is:

```text
CO(GT)
```

where the dataset provides a reference CO measurement.

---

# 📦 V2 Dataset

V2 uses the:

**UCI Air Quality Dataset**

The raw dataset contains:

```text
9,471 rows
17 columns
```

The UCI dataset uses:

```text
-200
```

as a missing-value sentinel.

These values were converted to missing values and removed from the required calibration dataset.

---

# 🧹 V2 Data Cleaning

Original dataset:

```text
9,471 rows
```

After removing rows with missing required measurements:

```text
7,344 rows
```

The final calibration dataset contains:

```text
7,344 measurements
```

---

# 🎯 V2 Calibration Target

Target:

```text
CO(GT)
```

Input features:

```text
PT08.S1(CO)
PT08.S2(NMHC)
PT08.S3(NOx)
PT08.S4(NO2)
PT08.S5(O3)
T
RH
AH
```

Therefore:

```text
8 input features
        ↓
Machine Learning Model
        ↓
Estimated CO concentration
```

---

# 📈 V2 Calibration Model

The primary V2 model uses:

```text
StandardScaler
+
LinearRegression
```

The model is trained using chronological data rather than a random split.

This better represents a real deployment scenario where the model is trained on earlier observations and used on later observations.

---

# 📊 V2 Model Performance

Using a chronological 75/25 split:

```text
Training samples: 5,508
Testing samples: 1,836
```

Results:

| Metric | Result |
| ------ | -----: |
| MAE    | 0.3693 |
| RMSE   | 0.5577 |
| R²     | 0.8311 |

These metrics describe regression performance.

**R² = 0.8311 should not be interpreted as 83.11% calibration accuracy.**

---

# 🌲 Random Forest Experiment

A Random Forest regression model was also evaluated.

Results:

| Model             |    MAE |   RMSE |     R² |
| ----------------- | -----: | -----: | -----: |
| Linear Regression | 0.3693 | 0.5577 | 0.8311 |
| Random Forest     | 0.4094 | 0.6245 | 0.7882 |

The Random Forest model performed worse on the selected chronological validation split.

Therefore, the Linear Regression pipeline was retained as the V2 model.

---

# 🔬 V2 Feature Analysis

Feature importance was examined using the coefficients of the standardized linear model.

The largest predictive contributions were:

| Feature       | Coefficient |
| ------------- | ----------: |
| PT08.S2(NMHC) |   +1.352226 |
| PT08.S1(CO)   |   +0.409305 |
| PT08.S4(NO2)  |   −0.199773 |
| T             |   −0.186121 |
| PT08.S3(NOx)  |   +0.182130 |
| AH            |   +0.059159 |
| PT08.S5(O3)   |   −0.047925 |
| RH            |   −0.000615 |

These coefficients are predictive relationships within the trained model and should not be interpreted as causal relationships.

---

# 🧪 V2 Feature Reduction Experiment

Different feature subsets were evaluated.

| Features |    MAE |   RMSE |     R² |
| -------- | -----: | -----: | -----: |
| All 8    | 0.3693 | 0.5577 | 0.8311 |
| Top 5    | 0.3753 | 0.5608 | 0.8292 |
| Top 3    | 0.4231 | 0.6075 | 0.7996 |
| Top 2    | 0.4504 | 0.6136 | 0.7955 |

The full eight-feature model was retained.

---

# 💾 V2 Model

The final model is stored as:

```text
models/v2/co_calibration_model.joblib
```

The original V2 `.pkl` model is also retained for compatibility with the earlier V2 application.

---

# 🖥️ V2 Streamlit Application

V2 provides a calibration interface where users enter sensor measurements and receive an estimated CO value.

The application provides:

* Sensor input fields
* CO prediction
* Raw model prediction
* Non-negative post-processing constraint
* Validation metrics
* Target range information
* Calibration record display
* CSV download

Example workflow:

```text
Sensor Measurements
        ↓
V2 Calibration Model
        ↓
Estimated CO
        ↓
Display Result
```

The non-negative output constraint is a post-processing rule and does not by itself prove physical calibration validity.

---

# 🏭 V3 — Calibration Management System

## Objective

V3 transforms the V2 prediction model into a small calibration management platform.

The system introduces persistent instrument and calibration records.

---

# 🗄️ V3 Database

V3 uses:

```text
SQLite
+
SQLAlchemy
```

Database location:

```text
database/calibration.db
```

The local database is intentionally excluded from Git because it contains local runtime/test records.

The database schema is defined in:

```text
src/v3/models.py
```

---

# 🔧 V3 Instrument Management

The system supports multiple instruments.

Each instrument contains:

```text
Instrument ID
Name
Manufacturer
Model
Serial Number
Instrument Type
Status
Created At
```

Supported operations include:

* Register instrument
* Edit instrument
* Activate instrument
* Deactivate instrument
* Select instrument
* View instrument information
* Maintain instrument-specific calibration history

Serial numbers are protected against duplicates.

---

# 🧪 V3 Calibration Workflow

The V3 calibration workflow is:

```text
Select Instrument
       ↓
Enter Sensor Measurements
       ↓
V2 ML Model
       ↓
Estimated CO
       ↓
Enter Reference CO
       ↓
Calculate Error
       ↓
Compare Against Tolerance
       ↓
PASS / FAIL
       ↓
Save Calibration Record
```

The error is calculated as:

```text
Error = Estimated Value − Reference Value
```

The absolute error is compared with the configured tolerance.

```text
Absolute Error ≤ Tolerance
        ↓
      PASS

Absolute Error > Tolerance
        ↓
      FAIL
```

---

# 📋 V3 Calibration Records

Each calibration record stores:

```text
Record ID
Instrument ID
Measurement Time
Model Version
Estimated Value
Reference Value
Error
Tolerance
Status
Created At
```

This provides an audit trail for calibration activity.

---

# 📊 V3 Dashboard

The V3 dashboard provides:

* Total calibrations
* PASS count
* FAIL count
* Pass rate
* Latest calibration status
* Calibration trends
* Calibration history
* Instrument information

The system supports instrument-specific history so that records belonging to one instrument do not appear under another instrument.

---

# 📄 V3 Calibration Reports

V3 generates PDF calibration reports using:

```text
ReportLab
```

The report includes:

### Report Information

* Report generation time
* Calibration record ID
* Model version
* Measurement time

### Instrument Information

* Instrument name
* Manufacturer
* Model
* Serial number
* Instrument type
* Instrument status

### Calibration Result

* Estimated CO
* Reference CO
* Error
* Tolerance
* PASS/FAIL status

### Calibration Statistics

* Total calibrations
* PASS count
* FAIL count
* Pass rate
* Mean Absolute Error
* Average error
* Maximum absolute error

The report can be downloaded directly from the Streamlit application.

Both PASS and FAIL report generation have been tested.

---

# 🧪 V3 Validation and Testing

The V3 system was tested for:

* Database persistence
* Instrument creation
* Instrument editing
* Instrument activation/deactivation
* Duplicate serial protection
* Multi-instrument isolation
* Calibration record creation
* PASS calculation
* FAIL calculation
* Tolerance handling
* Zero-tolerance boundary
* Invalid reference values
* Invalid estimated values
* Invalid tolerance values
* Application restart persistence
* Calibration history
* PASS PDF reports
* FAIL PDF reports

The database and application were verified after restarting the Streamlit application.

---

# 🏗️ Architecture

The current system can be represented as:

```text
                         LAB CALIBRATION SYSTEM
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
            V1                   V2                   V3
             │                    │                    │
      Drift Analysis       ML Calibration       Management System
             │                    │                    │
      Batch Analysis        CO Prediction        Instruments
             │                    │                    │
      Temporal Testing     Reference CO          Calibration Records
             │                    │                    │
      Model Robustness      Regression            PASS / FAIL
                                  │                    │
                                  └────────┬───────────┘
                                           │
                                      SQLite DB
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                           Dashboard               PDF Reports
```

---

# 📁 Project Structure

```text
Lab-Calibration-System/
│
├── app.py
├── app_v2.py
├── app_v3.py
├── README.md
├── .gitignore
│
├── data/
│   ├── processed/
│   │   ├── sensor_data.csv
│   │   └── sensor_data_with_batch.csv
│   │
│   └── v2/
│       ├── AirQualityUCI.csv
│       ├── AirQualityUCI.xlsx
│       └── co_calibration_dataset.csv
│
├── models/
│   └── v2/
│       ├── co_calibration_model.pkl
│       └── co_calibration_model.joblib
│
├── results/
│   ├── drift_measurements.csv
│   ├── batch_performance.csv
│   ├── model_comparison.csv
│   ├── baseline_vs_corrected.png
│   ├── model_performance_over_time.png
│   │
│   └── v2/
│       └── actual_vs_predicted_co.png
│
├── src/
│   ├── download_data.py
│   ├── parse_data.py
│   ├── analyze_data.py
│   ├── visualize_data.py
│   ├── analyze_drift.py
│   ├── controlled_drift.py
│   ├── measure_drift.py
│   ├── drift_trend.py
│   ├── baseline_model.py
│   ├── time_based_baseline.py
│   ├── batch_performance.py
│   ├── drift_compensation.py
│   ├── feature_drift_correction.py
│   ├── compare_models.py
│   ├── plot_performance.py
│   │
│   ├── v2/
│   │   ├── prepare_data.py
│   │   ├── build_calibration_dataset.py
│   │   ├── baseline_calibration.py
│   │   ├── time_calibration_test.py
│   │   ├── analyze_prediction_errors.py
│   │   ├── random_forest_calibration.py
│   │   └── train_final_model.py
│   │
│   └── v3/
│       ├── database.py
│       ├── models.py
│       ├── init_database.py
│       ├── calibration_service.py
│       ├── calibration_report.py
│       ├── list_instruments.py
│       ├── list_calibrations.py
│       ├── test_instrument.py
│       ├── test_calibration.py
│       ├── test_calibration_service.py
│       └── test_validation.py
│
└── database/
    └── calibration.db
```

> `database/calibration.db` is a local runtime database and is excluded from Git.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/Nagesha-G/Lab-Calibration-System.git
```

```bash
cd Lab-Calibration-System
```

---

## 2. Create a virtual environment

Windows:

```cmd
python -m venv .venv
```

Activate:

```cmd
.venv\Scripts\activate
```

---

## 3. Install dependencies

```cmd
pip install pandas numpy scikit-learn matplotlib seaborn jupyter ucimlrepo sqlalchemy streamlit reportlab joblib
```

---

# ▶️ Running the Applications

## V1

```cmd
streamlit run app.py
```

---

## V2

```cmd
streamlit run app_v2.py
```

---

## V3

```cmd
streamlit run app_v3.py
```

---

# 🗄️ Initializing the V3 Database

From the project root:

```cmd
python -m src.v3.init_database
```

Expected output:

```text
Database initialized successfully.
Instrument table created.
```

---

# 🔎 Listing Instruments

```cmd
python -m src.v3.list_instruments
```

---

# 📋 Listing Calibration Records

```cmd
python -m src.v3.list_calibrations
```

---

# 🧪 Running V3 Validation Tests

```cmd
python -m src.v3.test_validation
```

Additional V3 test scripts are available under:

```text
src/v3/
```

---

# 🔬 Technologies Used

## Programming

* Python

## Data Science

* Pandas
* NumPy
* Scikit-learn

## Visualization

* Matplotlib
* Seaborn

## Machine Learning

* Linear Regression
* Logistic Regression
* Random Forest
* StandardScaler
* Scikit-learn Pipeline

## Application

* Streamlit

## Database

* SQLite
* SQLAlchemy

## Reporting

* ReportLab

## Development

* Git
* GitHub
* Jupyter Notebook

---

# ⚠️ Current Limitations

This project is currently a software prototype and should not be treated as a certified laboratory calibration system.

Important limitations include:

### V1

The UCI Gas Sensor Array Drift Dataset is primarily useful for studying sensor drift and classification behavior.

Its class labels should not be interpreted as physical calibration reference values.

### V2

The calibration model is trained on the UCI Air Quality dataset.

Model performance depends on the distribution and quality of that dataset.

### V3

The system does not yet provide:

* Certified metrology workflows
* Laboratory accreditation
* Traceability to certified reference standards
* Automated hardware communication
* Real-time instrument communication
* Automated recalibration
* Sensor-specific physical calibration curves
* Production-grade authentication/authorization
* Distributed deployment
* Comprehensive automated test coverage

Therefore, V3 should currently be considered a **calibration management prototype**, not a certified calibration platform.

---

# 🛣️ Roadmap

## ✅ V1 — Sensor Drift Analysis

Completed.

* Dataset ingestion
* Sensor feature analysis
* Batch analysis
* Drift measurement
* Temporal validation
* Drift compensation experiments
* Streamlit dashboard

---

## ✅ V2 — Machine Learning Calibration

Completed.

* Air Quality dataset
* Missing-value cleaning
* Calibration dataset construction
* Regression model
* Chronological validation
* Error analysis
* Feature analysis
* Model comparison
* Final model
* Streamlit prediction application

---

## ✅ V3 — Calibration Management System

Completed.

* SQLite database
* SQLAlchemy ORM
* Instrument management
* Multiple instruments
* Calibration records
* Reference-value comparison
* Tolerance-based PASS/FAIL
* Calibration history
* Dashboard statistics
* Calibration trends
* PDF calibration reports
* Validation testing
* Git release `v3.0.0`

---

## 🔜 V4 — API + Scheduling

Planned.

Potential capabilities:

```text
FastAPI
REST endpoints
Calibration API
Instrument API
Calibration history API
Background jobs
Scheduled calibration checks
Automated notifications
API authentication
```

---

## 🔜 V5 — Multi-Instrument Platform

Planned.

Potential capabilities:

```text
Multiple instrument types
Instrument fleets
Centralized calibration management
Role-based access
Organization management
Audit logs
Calibration certificates
Advanced reporting
```

---

## 🔜 V6 — Real Hardware + Laboratory Deployment

Long-term goal.

Potential capabilities:

```text
Real instrument communication
Serial / USB communication
Industrial protocols
Real-time sensor acquisition
Automated calibration procedures
Reference instruments
Laboratory workflows
Hardware-in-the-loop testing
Traceability
Production deployment
```

---

# 🏷️ Releases

Current releases:

```text
v1.0.0 — Sensor Drift Analysis
v2.0.0 — Machine Learning Calibration
v3.0.0 — Calibration Management System
```

The V3 release is tagged in Git as:

```text
v3.0.0
```

---

# 📚 Dataset Sources

## UCI Gas Sensor Array Drift Dataset

Used for V1 sensor drift and temporal robustness experiments.

Dataset:

[https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset)

---

## UCI Air Quality Dataset

Used for V2 CO calibration modeling.

Dataset:

[https://archive.ics.uci.edu/dataset/360/air+quality](https://archive.ics.uci.edu/dataset/360/air+quality)

---

# 📌 Engineering Philosophy

The project follows a progressive engineering approach:

```text
Observe
  ↓
Measure
  ↓
Model
  ↓
Validate
  ↓
Integrate
  ↓
Persist
  ↓
Report
  ↓
Automate
```

A model is not considered successful simply because it performs well on a random train/test split.

The project therefore emphasizes:

* Temporal validation
* Error measurement
* Distribution shift
* Model comparison
* Rejection of ineffective corrections
* Persistent calibration records
* Explicit tolerance criteria
* Reproducible workflows

---

# 👨‍💻 Author

**Nagesh**

Lab Calibration System

Built as an evolving engineering project covering:

```text
Data Science
Machine Learning
Sensor Analytics
Calibration
Database Engineering
Software Engineering
Streamlit
API Development
Laboratory Automation
```

---

# ⭐ Project Status

```text
V1  ✅ Complete
V2  ✅ Complete
V3  ✅ Complete
V4  🔜 Next
V5  🔜 Planned
V6  🔜 Long-term
```

The current stable milestone is:

```text
V3.0.0
```

---

## License

Review the individual dataset licenses/terms before redistributing datasets or using them commercially.

The software project's license should be defined separately before public/commercial distribution.

````

### One important correction

I intentionally **did not claim that V3 is a certified laboratory calibration system**. What you have built is a strong prototype with a real database, ML model integration, tolerance-based calibration workflow, audit history, and PDF reporting. Certification, traceability, hardware integration, and metrology controls are still future work.



