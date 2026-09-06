# 🔬 Lab Calibration System

## Sensor Drift Analysis & Calibration Prototype

A Python-based machine-learning prototype for analyzing sensor drift, measuring temporal distribution shift, and evaluating drift-compensation strategies on sensor-array data.

> **Current version: V1 — Sensor Drift Analysis Prototype**

---

## 🎯 Project Overview

Sensors can behave differently over time.

A machine-learning model may perform extremely well when training and testing data are randomly mixed, but its performance can decrease when it encounters measurements collected later under changed sensor conditions.

This project investigates that problem from first principles:

```text
Sensor measurements
        ↓
Data processing
        ↓
Drift analysis
        ↓
Machine-learning baseline
        ↓
Future-batch validation
        ↓
Drift compensation experiment
        ↓
Performance comparison
        ↓
User-facing Streamlit dashboard
```

The objective of V1 is to determine whether sensor measurements exhibit temporal drift and whether a simple compensation strategy can improve model generalization to future batches.

---

# 🚀 V1 Results

## Random-Split Baseline

A Logistic Regression classifier with feature standardization achieved:

**98.99% accuracy**

on a random 80/20 train-test split.

However, random splitting can allow measurements from similar time periods to appear in both training and testing data.

Therefore, a stricter temporal evaluation was performed.

---

## ⏱️ Future-Batch Evaluation

The model was trained using:

```text
Batches 1–7
```

and evaluated on:

```text
Batches 8–10
```

Results:

| Batch | Samples | Accuracy |
| ----: | ------: | -------: |
|     8 |     294 |   91.50% |
|     9 |     470 |   74.04% |
|    10 |    3600 |   72.53% |

This demonstrates a substantial reduction in model performance on later unseen batches.

---

# 📊 Sensor Drift Analysis

The project also measures changes in sensor-derived features across batches while controlling for gas class.

Examples of measured batch-1 → batch-10 changes include:

| Feature    | Class | Percentage Change |
| ---------- | ----: | ----------------: |
| feature_2  |     2 |          +128.01% |
| feature_3  |     4 |           −89.89% |
| feature_1  |     4 |           −89.69% |
| feature_33 |     5 |           +83.79% |
| feature_3  |     6 |           −82.34% |

These values indicate substantial temporal changes in sensor-derived measurements.

> These measurements should be interpreted as evidence of distribution shift / sensor response change, not automatically as physical calibration error.

---

# 🔧 Drift Compensation Experiment

A feature-wise linear drift correction method was tested.

Conceptually:

```text
Observed sensor response
          ↓
Estimate feature drift trend
          ↓
Remove estimated drift
          ↓
Train classifier
          ↓
Evaluate future batches
```

The result was **negative**.

| Batch | Baseline | Corrected |    Change |
| ----: | -------: | --------: | --------: |
|     8 |   91.50% |    90.48% |  −1.02 pp |
|     9 |   74.04% |    62.13% | −11.91 pp |
|    10 |   72.53% |    62.92% |  −9.61 pp |

### Engineering Decision

❌ **The tested correction method was rejected.**

The correction reduced performance on future batches rather than improving it.

This is an intentional experimental result rather than a failed project: the experiment demonstrates why drift-compensation methods must be evaluated against future data before deployment.

---

# 🖥️ Streamlit Application

The project includes a local Streamlit dashboard designed to make the analysis understandable without reading the Python source code.

The dashboard provides:

### 🏠 Dashboard

* Number of measurements
* Number of sensor features
* Number of batches
* Number of gas classes
* Model performance
* System diagnosis

### 📊 Sensor Drift

* Feature selection
* Batch-level sensor response visualization
* Quantitative drift measurements

### 🧠 Model Performance

* Future-batch accuracy
* Batch-by-batch performance
* Performance degradation visualization

### 🔧 Compensation Experiment

* Baseline vs corrected performance
* Compensation improvement
* Engineering decision

### 🔎 Data Explorer

* Batch filtering
* Gas-class filtering
* Raw processed measurements

---

# 🧰 Technology Stack

* **Python**
* **Pandas**
* **NumPy**
* **Scikit-learn**
* **Matplotlib**
* **Seaborn**
* **Streamlit**
* **Jupyter Notebook**
* **Git / GitHub**

---

# 📁 Project Structure

```text
lab-calibration-system/
│
├── app.py
├── README.md
│
├── data/
│   ├── raw/
│   └── processed/
│       └── sensor_data_with_batch.csv
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
│   └── compare_models.py
│
├── models/
│
├── results/
│   ├── drift_measurements.csv
│   ├── drift_trends.csv
│   ├── batch_performance.csv
│   ├── model_comparison.csv
│   └── *.png
│
└── notebooks/
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Move into the project:

```bash
cd lab-calibration-system
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter streamlit
```

---

# ▶️ Running the Analysis

Run the data processing pipeline:

```bash
python src/parse_data.py
```

Run drift analysis:

```bash
python src/analyze_drift.py
```

Run controlled drift analysis:

```bash
python src/controlled_drift.py
```

Measure drift:

```bash
python src/measure_drift.py
```

Run the baseline model:

```bash
python src/baseline_model.py
```

Run temporal validation:

```bash
python src/time_based_baseline.py
```

Run the compensation experiment:

```bash
python src/feature_drift_correction.py
```

Compare models:

```bash
python src/compare_models.py
```

---

# 🖥️ Run the Dashboard

Start Streamlit:

```bash
streamlit run app.py
```

The application runs locally and provides an interactive interface for exploring the sensor data and model results.

---

# 🧠 Key Learning

One of the most important findings from V1 is:

> **A very high random-split accuracy does not necessarily mean that a sensor-based machine-learning system will generalize to future sensor conditions.**

The temporal evaluation exposed a significant performance decrease.

The first compensation strategy also failed to recover that performance.

This creates a clear direction for V2.

---

# 🔬 Limitations

This V1 project is a **sensor-drift research prototype**, not a production laboratory calibration system.

The current dataset provides sensor-derived measurements and gas-class labels. Those labels should not be treated as direct physical reference values for calibration regression.

Therefore, V1 does not claim to produce a calibrated physical quantity such as concentration, temperature, pressure, or mass.

A proper calibration system requires trustworthy reference measurements paired with sensor observations.

---

# 🛣️ Roadmap

## V1 — Sensor Drift Prototype

* [x] Data acquisition
* [x] Data parsing
* [x] Data validation
* [x] Drift analysis
* [x] Controlled drift analysis
* [x] Drift measurement
* [x] ML baseline
* [x] Temporal validation
* [x] Compensation experiment
* [x] Model comparison
* [x] Streamlit dashboard

## V2 — Calibration Software

* [ ] Acquire appropriate reference-value dataset
* [ ] Pair sensor measurements with reference measurements
* [ ] Build calibration regression models
* [ ] Compare calibration algorithms
* [ ] Evaluate calibration error
* [ ] Save trained calibration model
* [ ] Build inference pipeline
* [ ] Integrate calibration into Streamlit

## V3 — Instrument Management

* [ ] Instrument database
* [ ] Sensor/instrument profiles
* [ ] Calibration history
* [ ] Model versioning
* [ ] Calibration records

## V4 — Automation

* [ ] API
* [ ] Scheduled calibration analysis
* [ ] Automated reports
* [ ] Drift alerts

## V5 — Multi-Instrument Platform

* [ ] Multiple instruments
* [ ] Multiple sensor types
* [ ] Centralized monitoring
* [ ] Model management

## V6 — Hardware Integration

* [ ] Real sensor hardware
* [ ] Live sensor logs
* [ ] Real reference measurements
* [ ] Laboratory deployment

---

# 📚 Dataset

This V1 prototype uses the **UCI Gas Sensor Array Drift Dataset** for sensor-drift analysis.

Dataset source:

UCI Machine Learning Repository

https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift

Please review the dataset's licensing and usage conditions before redistributing the dataset or using it commercially.

---

# 📌 Project Status

**Version:** V1

**Status:** Prototype completed / V1 evaluation

**Current focus:** Sensor drift analysis and future-batch model robustness

**Next milestone:** V2 — physically grounded calibration software

---

# 👨‍💻 Author
**Nagesha G**
Built as an end-to-end machine-learning and software-engineering project covering:

```text
Data
 ↓
Analysis
 ↓
Machine Learning
 ↓
Experimentation
 ↓
Evaluation
 ↓
Visualization
 ↓
Application
```
