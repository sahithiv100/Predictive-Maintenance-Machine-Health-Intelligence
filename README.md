# Predictive Maintenance & Machine Health Intelligence System
**ABC Automotive Components Pvt. Ltd.**  
*Automotive Component Manufacturing — Plant 01 (Precision Division)*

---

## 🎯 Executive Overview
Unexpected equipment failures in automotive component manufacturing lead to acute production downtime, expensive emergency overhauls, and delivery penalties to automotive OEMs. 

The **Predictive Maintenance & Machine Health Intelligence System** is an end-to-end, AI-powered industrial monitoring application. It continuously analyzes high-frequency sensor telemetry, historical maintenance records, machine warranty status, and production schedules across **105 machines** to detect abnormal behavior, predict potential equipment failures before functional breakdown, calculate dynamic asset health scores, and prescribe preventive work orders.

---

## 🚀 Live System Access
The application is running live:
- **Local Web Application URL:** [http://localhost:8000](http://localhost:8000)
- **API Documentation (FastAPI Interactive Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🏭 Company & Fleet Environment (Section 1)
- **Company:** ABC Automotive Components Pvt. Ltd.
- **Industry:** Tier-1 Automotive Component Manufacturing (Engine Blocks, Transmissions, Chassis, Stamping, Powertrain)
- **Fleet Scope:** **105 Production Machines** across 8 industrial categories:
  1. **CNC Machines** (18 units: `CNC-001` to `CNC-018`) — Precision Machining Department
  2. **Hydraulic Presses** (14 units: `HYD-001` to `HYD-014`) — Stamping & Press Department
  3. **Injection Moulding Machines** (13 units: `IMM-001` to `IMM-013`) — Molding & Polymer Department
  4. **Industrial Compressors** (12 units: `CMP-001` to `CMP-012`) — Compressed Air Utility
  5. **Conveyor Motors** (14 units: `CNV-001` to `CNV-014`) — Assembly & Conveyance
  6. **Robotic Welding Machines** (13 units: `ROB-001` to `ROB-013`) — Robotic Fabrication
  7. **Lathe Machines** (11 units: `LTH-001` to `LTH-011`) — Toolroom Turning
  8. **Milling Machines** (10 units: `MIL-001` to `MIL-010`) — Toolroom Milling

Each machine record tracks:
`Machine_ID`, `Machine_Name`, `Machine_Type`, `Department`, `Installation_Date`, `Machine_Age`, `Manufacturer`, `Model`, `Warranty_Status`, `Operating_Hours`, `Maximum_Rated_Capacity`, `Current_Utilization`, `Production_Line`, `Shift_Pattern`, `Criticality_Level`, `Last_Maintenance_Date`, `Next_Scheduled_Maintenance_Date`, `Number_of_Previous_Failures`, `Total_Maintenance_Cost`, `Total_Downtime_Hours`, `Current_Machine_Health_Score`, `Current_Failure_Probability`, `Current_Risk_Level`.

---

## 📊 Core Architectural Features

### 1. Synthetic Data & Realistic Sensor Dynamics (Section 2 & 26)
- **12 Months Historical Data:** 606 maintenance records and 2,100 production schedule shifts.
- **Machine-Specific Physical Ranges:** 10 continuous sensors (Temperature °C, Vibration mm/s, RPM, Pressure bar, Current A, Voltage V, Power kW, Lubricant Level %, Humidity %, Load %).
- **Preset Failure Scenarios:**
  - **`CNC-004` (Critical):** Bearing / Spindle Failure. Temperature: 88.4°C (+29% deviation), Vibration: 7.85 mm/s (+144% deviation), Oil: 31.8% (critically low), RPM: 4,850.
  - **`CMP-012` (Critical):** Compressor Overheating & Pressure Loss. Pressure: 14.8 bar, Temp: 96.2°C, Power: 58.4 kW.
  - **`CNV-023` (High Risk):** Conveyor Motor Overload. RPM drops to 410, Current spikes to 27.8A, Vibration: 6.5 mm/s.
  - **`HYD-017` (High Risk):** Hydraulic Overheating & Proportional Valve Leak. Pressure oscillation: 248 bar, Temp: 82.5°C.
  - **`ROB-008` (High Risk):** Welding Arm Servo Imbalance & Cable Harness Wear. Current: 184A, Vibration: 4.85 mm/s.
  - **`IMM-006` (High Risk):** Barrel Heating Element & Thermal Clog. Temp: 241.5°C, Pressure: 218 bar.

### 2. Multi-Factor Dynamic Machine Health Score (Section 4)
Calculated continuously from 0–100 using weighted reliability factors:
- **Sensor Condition:** 35%
- **Maintenance Condition:** 20%
- **Machine Age:** 10%
- **Utilization & Production Load:** 15%
- **Operating Hours:** 10%
- **Failure History:** 10%

**Health Bands:** Excellent (90–100) | Good (75–89) | Warning (60–74) | Poor (40–59) | Critical (0–39).

### 3. Machine Learning Failure Prediction & Type Diagnosis (Section 5 & 6)
- **Algorithm:** Scikit-learn `RandomForestClassifier` & `GradientBoostingClassifier` trained on normalized multi-sensor feature space.
- **Horizon:** 7-Day failure probability (0–100%).
- **Failure Type Diagnosis:** Physical pattern matching + ML mapping (High Temp + High Vib → Bearing Failure; High Current + Low RPM → Motor Overload; Low Oil + High Temp → Lubrication Failure; High Pressure + High Temp → Compressor/Pressure Failure).

### 4. Explainable AI (XAI) (Section 19)
Transparent mathematical risk attribution:
- Example: **`CNC-004`** (87.2% Failure Probability):
  - `+25.0%` Elevated Vibration (7.85 mm/s vs 2.4 mm/s baseline)
  - `+22.5%` High Operating Temperature (88.4°C vs 61.0°C baseline)
  - `+16.2%` Low Lubricant / Oil Level (31.8% vs 80.0% nominal)
  - `+12.6%` High Production Utilization (94% load)
  - `+5.8%` Maintenance Overdue (18 days past due)
  - `+5.1%` Asset Age (4.2 years)

### 5. Automated Machine Report Cards & PDF Generation (Section 13, 14 & 27)
- **Full Report Card Layout:** Conforms to industrial audit standards with asset specs, telemetry deviations, top risk factors, recommended directives, and consequences if ignored.
- **PDF Generation:** Powered by Python `reportlab` with downloadable high-resolution single cards (`/api/machines/{id}/pdf`) and bulk compiled PDFs (`/api/reports/bulk-pdf`).
- **On-Screen Print Support:** One-click modal print view formatted for A4/Letter printers.

### 6. What-If Operating Scenario Simulator (Section 20)
- Interactive sliders for **Temperature**, **Vibration**, **RPM**, **Production Load**, **Oil Level**, and **Days Since Last Service**.
- Instant recalculation of Health Score, Failure Probability, and Prescriptive Directives with visual delta indicators.

### 7. Production Impact & Business ROI (Section 16 & 18)
- **Production Impact:** Quantifies downtime hours, automotive components at risk, and financial loss across 5 production lines.
- **Financial Model (INR ₹):**
  - Unmitigated Breakdown Cost: **₹18,50,000**
  - Predictive Maintenance Cost: **₹7,20,000**
  - Avoided Downtime Value: **₹11,30,000**
  - Potential Net Annual Savings: **₹11,30,000** (**+156.9% ROI**)

### 8. Data Quality & Pipeline Audit (Section 24)
- **Data Quality Score:** **98.4%** across 27,300 telemetry data points.
- 8-stage automated processing: Timestamp validation, Machine ID validation, forward-fill missing value imputation, primary key deduplication, adaptive Z-score outlier detection (>3.0σ), and normalization.

---

## 🛠️ Technology Stack
- **Backend:** Python 3.13, FastAPI, Uvicorn, Scikit-learn, Pandas, NumPy, ReportLab
- **Frontend:** HTML5, Modern Responsive Single Page Architecture (SPA), Tailwind CSS, FontAwesome 6, Chart.js 4.4
- **Data Engine:** Synthetic telemetry time-series generator with CSV and JSON persistence

---

## 📂 Project Structure
```
predictive_maintenance_system/
├── app.py                     # FastAPI REST API server & static file host
├── ml_engine.py               # Scikit-learn models, health scoring & XAI attribution
├── pdf_generator.py           # ReportLab PDF report card and management report generator
├── data_generator.py          # Synthetic dataset generator (105 machines, 6-12 months data)
├── requirements.txt           # Python dependencies
├── run_system.bat             # Windows one-click startup launcher
├── data/                      # Generated CSV and JSON data tables
│   ├── machines_master.json
│   ├── latest_sensors.json
│   ├── telemetry_history.json
│   ├── maintenance_history.json
│   ├── production_schedule.json
│   └── data_quality.json
├── reports_export/            # Output folder for generated PDF reports
└── static/                    # Frontend SPA assets
    ├── index.html             # Industrial dark-theme monitoring UI
    ├── css/styles.css         # Custom industrial styling and print stylesheets
    └── js/app.js              # SPA router, Chart.js controllers, What-If simulation
```

---

## 🏃 Running the Application
To run or restart the system manually at any time:
```powershell
cd C:\Users\DELL\.gemini\antigravity\scratch\predictive_maintenance_system
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in any web browser.
