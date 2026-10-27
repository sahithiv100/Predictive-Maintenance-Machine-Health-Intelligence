"""
Synthetic Data Generator for Apex AutoForge Technologies Ltd.
Company: Apex AutoForge Technologies Ltd. (Single Company Focus)
Industry: Tier-1 Automotive Component Manufacturing (Powertrain, Transmission & Chassis)

Generates:
1. Machine Master Data (105 machines across 8 categories)
2. Sensor Baseline Specifications per machine type
3. 6-12 Months Historical & Telemetry Sensor Data
4. Maintenance History Records (600+ records)
5. Production Schedules (2,100 records across 5 production lines)
6. Data Quality Diagnostics (Missing values, Duplicates, Outliers)
"""

import json
import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

BASE_DIR = r"C:\Users\DELL\.gemini\antigravity\scratch\predictive_maintenance_system"
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

COMPANY_NAME = "Apex AutoForge Technologies Ltd."
PLANT_NAME = "Apex Smart Manufacturing Plant 01 (Powertrain & Precision Hub)"

MACHINE_TYPES = [
    {
        "type": "CNC Machine",
        "prefix": "CNC",
        "dept": "Precision Machining",
        "count": 18,
        "mfrs": ["Haas Automation", "DMG Mori", "Mazak", "Fanuc"],
        "models": ["Apex VF-4SS", "NTX 2000 Pro", "VCN-530C", "Robodrill D21"],
        "rated_cap": "120 pcs/hr",
        "sensors": {
            "temp": {"normal": (50, 72), "warn": (72, 82), "crit": (82, 95), "unit": "°C"},
            "rpm": {"normal": (2500, 5200), "warn": (5200, 5800), "crit": (5800, 6500), "unit": "RPM"},
            "vibration": {"normal": (1.0, 3.8), "warn": (3.8, 6.0), "crit": (6.0, 11.0), "unit": "mm/s"},
            "pressure": {"normal": (4.5, 6.8), "warn": (6.8, 7.8), "crit": (7.8, 10.0), "unit": "bar"},
            "current": {"normal": (12, 28), "warn": (28, 36), "crit": (36, 48), "unit": "A"},
            "voltage": {"normal": (395, 415), "warn": (380, 425), "crit": (360, 440), "unit": "V"},
            "power": {"normal": (8, 22), "warn": (22, 28), "crit": (28, 38), "unit": "kW"},
            "oil_level": {"normal": (65, 95), "warn": (45, 65), "crit": (15, 45), "unit": "%"},
            "humidity": {"normal": (40, 60), "warn": (60, 75), "crit": (75, 90), "unit": "%"},
            "load": {"normal": (55, 80), "warn": (80, 92), "crit": (92, 100), "unit": "%"}
        }
    },
    {
        "type": "Hydraulic Press",
        "prefix": "HYD",
        "dept": "Stamping & Press",
        "count": 14,
        "mfrs": ["Schuler Group", "Aida Engineering", "Komatsu Press"],
        "models": ["Apex HP-500T", "Servo-Press 400", "KP-300 Heavy"],
        "rated_cap": "80 strokes/hr",
        "sensors": {
            "temp": {"normal": (45, 68), "warn": (68, 78), "crit": (78, 92), "unit": "°C"},
            "rpm": {"normal": (0, 450), "warn": (450, 550), "crit": (550, 700), "unit": "RPM"},
            "vibration": {"normal": (0.8, 3.2), "warn": (3.2, 5.2), "crit": (5.2, 9.0), "unit": "mm/s"},
            "pressure": {"normal": (120, 210), "warn": (210, 240), "crit": (240, 275), "unit": "bar"},
            "current": {"normal": (18, 38), "warn": (38, 46), "crit": (46, 60), "unit": "A"},
            "voltage": {"normal": (400, 418), "warn": (385, 425), "crit": (365, 440), "unit": "V"},
            "power": {"normal": (15, 34), "warn": (34, 42), "crit": (42, 55), "unit": "kW"},
            "oil_level": {"normal": (70, 95), "warn": (50, 70), "crit": (20, 50), "unit": "%"},
            "humidity": {"normal": (40, 65), "warn": (65, 80), "crit": (80, 92), "unit": "%"},
            "load": {"normal": (60, 85), "warn": (85, 94), "crit": (94, 100), "unit": "%"}
        }
    },
    {
        "type": "Injection Moulding Machine",
        "prefix": "IMM",
        "dept": "Molding & Polymer",
        "count": 13,
        "mfrs": ["Engel Machinery", "KraussMaffei", "Arburg", "Sumitomo"],
        "models": ["victory 330", "Apex GX 450", "Allrounder 520", "SE-EV 280"],
        "rated_cap": "150 parts/hr",
        "sensors": {
            "temp": {"normal": (175, 215), "warn": (215, 230), "crit": (230, 255), "unit": "°C"},
            "rpm": {"normal": (80, 220), "warn": (220, 280), "crit": (280, 350), "unit": "RPM"},
            "vibration": {"normal": (0.5, 2.5), "warn": (2.5, 4.2), "crit": (4.2, 7.5), "unit": "mm/s"},
            "pressure": {"normal": (110, 185), "warn": (185, 215), "crit": (215, 250), "unit": "bar"},
            "current": {"normal": (28, 52), "warn": (52, 64), "crit": (64, 80), "unit": "A"},
            "voltage": {"normal": (398, 416), "warn": (380, 425), "crit": (360, 440), "unit": "V"},
            "power": {"normal": (20, 45), "warn": (45, 58), "crit": (58, 72), "unit": "kW"},
            "oil_level": {"normal": (68, 92), "warn": (50, 68), "crit": (22, 50), "unit": "%"},
            "humidity": {"normal": (35, 55), "warn": (55, 70), "crit": (70, 88), "unit": "%"},
            "load": {"normal": (65, 88), "warn": (88, 95), "crit": (95, 100), "unit": "%"}
        }
    },
    {
        "type": "Industrial Compressor",
        "prefix": "CMP",
        "dept": "Compressed Air Utility",
        "count": 12,
        "mfrs": ["Atlas Copco", "Ingersoll Rand", "Kaeser Kompressoren"],
        "models": ["GA 75 VSD+", "Sierra Oil-Free", "CSD 125 Heavy"],
        "rated_cap": "850 CFM",
        "sensors": {
            "temp": {"normal": (55, 78), "warn": (78, 88), "crit": (88, 104), "unit": "°C"},
            "rpm": {"normal": (1450, 2850), "warn": (2850, 3100), "crit": (3100, 3600), "unit": "RPM"},
            "vibration": {"normal": (1.2, 4.2), "warn": (4.2, 7.0), "crit": (7.0, 12.5), "unit": "mm/s"},
            "pressure": {"normal": (6.5, 10.5), "warn": (10.5, 12.8), "crit": (12.8, 16.0), "unit": "bar"},
            "current": {"normal": (22, 48), "warn": (48, 58), "crit": (58, 72), "unit": "A"},
            "voltage": {"normal": (396, 414), "warn": (380, 424), "crit": (360, 440), "unit": "V"},
            "power": {"normal": (18, 42), "warn": (42, 52), "crit": (52, 68), "unit": "kW"},
            "oil_level": {"normal": (60, 90), "warn": (42, 60), "crit": (18, 42), "unit": "%"},
            "humidity": {"normal": (40, 60), "warn": (60, 75), "crit": (75, 90), "unit": "%"},
            "load": {"normal": (50, 80), "warn": (80, 92), "crit": (92, 100), "unit": "%"}
        }
    },
    {
        "type": "Conveyor Motor",
        "prefix": "CNV",
        "dept": "Assembly & Conveyance",
        "count": 14,
        "mfrs": ["SEW-Eurodrive", "Siemens Drive", "Nord Drivesystems"],
        "models": ["MoviGear B", "Simogear 2KJ3", "NORDBLOC.1"],
        "rated_cap": "250 m/min",
        "sensors": {
            "temp": {"normal": (40, 62), "warn": (62, 72), "crit": (72, 88), "unit": "°C"},
            "rpm": {"normal": (850, 1650), "warn": (650, 850), "crit": (350, 650), "unit": "RPM"},
            "vibration": {"normal": (0.6, 2.8), "warn": (2.8, 4.8), "crit": (4.8, 8.5), "unit": "mm/s"},
            "pressure": {"normal": (1.0, 2.5), "warn": (2.5, 3.5), "crit": (3.5, 5.0), "unit": "bar"},
            "current": {"normal": (6, 16), "warn": (16, 22), "crit": (22, 32), "unit": "A"},
            "voltage": {"normal": (400, 415), "warn": (385, 422), "crit": (365, 440), "unit": "V"},
            "power": {"normal": (4, 11), "warn": (11, 15), "crit": (15, 22), "unit": "kW"},
            "oil_level": {"normal": (70, 95), "warn": (50, 70), "crit": (25, 50), "unit": "%"},
            "humidity": {"normal": (40, 65), "warn": (65, 80), "crit": (80, 90), "unit": "%"},
            "load": {"normal": (45, 75), "warn": (75, 88), "crit": (88, 100), "unit": "%"}
        }
    },
    {
        "type": "Robotic Welding Machine",
        "prefix": "ROB",
        "dept": "Robotic Fabrication",
        "count": 13,
        "mfrs": ["Fanuc Robotics", "Kuka Robotics", "ABB Robotics", "Yaskawa Motoman"],
        "models": ["ARC Mate 120iD", "KR CYBERTECH Arc", "IRB 2600ID", "AR2010"],
        "rated_cap": "65 welds/hr",
        "sensors": {
            "temp": {"normal": (38, 62), "warn": (62, 74), "crit": (74, 90), "unit": "°C"},
            "rpm": {"normal": (100, 450), "warn": (450, 600), "crit": (600, 750), "unit": "RPM"},
            "vibration": {"normal": (0.4, 2.2), "warn": (2.2, 4.0), "crit": (4.0, 7.2), "unit": "mm/s"},
            "pressure": {"normal": (4.0, 6.5), "warn": (6.5, 7.5), "crit": (7.5, 9.5), "unit": "bar"},
            "current": {"normal": (65, 140), "warn": (140, 175), "crit": (175, 230), "unit": "A"},
            "voltage": {"normal": (24, 38), "warn": (38, 44), "crit": (44, 52), "unit": "V"},
            "power": {"normal": (8, 22), "warn": (22, 28), "crit": (28, 38), "unit": "kW"},
            "oil_level": {"normal": (70, 95), "warn": (52, 70), "crit": (25, 52), "unit": "%"},
            "humidity": {"normal": (35, 55), "warn": (55, 70), "crit": (70, 85), "unit": "%"},
            "load": {"normal": (55, 82), "warn": (82, 92), "crit": (92, 100), "unit": "%"}
        }
    },
    {
        "type": "Lathe Machine",
        "prefix": "LTH",
        "dept": "Toolroom Turning",
        "count": 11,
        "mfrs": ["Mazak", "Doosan Machine Tools", "Okuma Corporation"],
        "models": ["Quick Turn 250", "PUMA GT2600", "GENOS L3000-e"],
        "rated_cap": "90 shafts/hr",
        "sensors": {
            "temp": {"normal": (45, 68), "warn": (68, 78), "crit": (78, 92), "unit": "°C"},
            "rpm": {"normal": (800, 2900), "warn": (2900, 3300), "crit": (3300, 3900), "unit": "RPM"},
            "vibration": {"normal": (0.9, 3.4), "warn": (3.4, 5.5), "crit": (5.5, 9.8), "unit": "mm/s"},
            "pressure": {"normal": (2.5, 5.0), "warn": (5.0, 6.2), "crit": (6.2, 8.0), "unit": "bar"},
            "current": {"normal": (10, 26), "warn": (26, 33), "crit": (33, 44), "unit": "A"},
            "voltage": {"normal": (398, 415), "warn": (382, 424), "crit": (362, 440), "unit": "V"},
            "power": {"normal": (7, 19), "warn": (19, 25), "crit": (25, 34), "unit": "kW"},
            "oil_level": {"normal": (65, 92), "warn": (45, 65), "crit": (20, 45), "unit": "%"},
            "humidity": {"normal": (40, 60), "warn": (60, 75), "crit": (75, 90), "unit": "%"},
            "load": {"normal": (50, 78), "warn": (78, 90), "crit": (90, 100), "unit": "%"}
        }
    },
    {
        "type": "Milling Machine",
        "prefix": "MIL",
        "dept": "Toolroom Milling",
        "count": 10,
        "mfrs": ["DMG Mori", "Hermle AG", "Makino Milling"],
        "models": ["CMX 600 V", "C 400", "F5 Vertical"],
        "rated_cap": "95 flanges/hr",
        "sensors": {
            "temp": {"normal": (48, 70), "warn": (70, 80), "crit": (80, 94), "unit": "°C"},
            "rpm": {"normal": (1800, 4400), "warn": (4400, 4900), "crit": (4900, 5600), "unit": "RPM"},
            "vibration": {"normal": (1.1, 3.6), "warn": (3.6, 5.8), "crit": (5.8, 10.2), "unit": "mm/s"},
            "pressure": {"normal": (3.0, 5.8), "warn": (5.8, 7.0), "crit": (7.0, 9.0), "unit": "bar"},
            "current": {"normal": (11, 28), "warn": (28, 35), "crit": (35, 46), "unit": "A"},
            "voltage": {"normal": (397, 416), "warn": (382, 423), "crit": (360, 440), "unit": "V"},
            "power": {"normal": (8, 21), "warn": (21, 27), "crit": (27, 36), "unit": "kW"},
            "oil_level": {"normal": (65, 94), "warn": (46, 65), "crit": (18, 46), "unit": "%"},
            "humidity": {"normal": (38, 62), "warn": (62, 75), "crit": (75, 88), "unit": "%"},
            "load": {"normal": (52, 80), "warn": (80, 90), "crit": (90, 100), "unit": "%"}
        }
    }
]

PRODUCTION_LINES = [
    {"id": "Line A", "name": "Engine Block Machining Line", "criticality_mult": 1.3},
    {"id": "Line B", "name": "Transmission Gear Line", "criticality_mult": 1.25},
    {"id": "Line C", "name": "Chassis & Suspension Sub-assembly", "criticality_mult": 1.1},
    {"id": "Line D", "name": "High-Speed Body Stamping Line", "criticality_mult": 1.2},
    {"id": "Line E", "name": "Powertrain Final Integration Line", "criticality_mult": 1.35}
]

SHIFT_PATTERNS = ["3 Shifts (24/7 Continuous)", "3 Shifts (Mon-Sat)", "2 Shifts (16h)", "2 Shifts (Mon-Fri)", "Weekend Intensive"]
CRITICALITY_LEVELS = ["Critical", "High", "Medium", "Low"]

PRESET_ANOMALIES = {
    "CNC-004": {
        "status": "Critical",
        "predicted_failure": "Bearing / Spindle Failure",
        "sensor_overrides": {"temp": 88.4, "vibration": 7.85, "oil_level": 31.8, "rpm": 4850.0, "current": 37.5, "load": 94.0},
        "days_overdue": 18,
        "historical_failures": 5,
        "failure_prob": 87.2,
        "health_score": 42.0,
        "risk_level": "Critical",
        "confidence": 92.5,
        "impact_downtime": 14.0,
        "units_at_risk": 1250,
        "breakdown_cost": 180000
    },
    "CMP-012": {
        "status": "Critical",
        "predicted_failure": "Compressor Overheating & Pressure System Failure",
        "sensor_overrides": {"temp": 96.2, "pressure": 14.8, "power": 58.4, "current": 64.2, "vibration": 8.4, "load": 96.0},
        "days_overdue": 14,
        "historical_failures": 4,
        "failure_prob": 83.5,
        "health_score": 38.5,
        "risk_level": "Critical",
        "confidence": 89.0,
        "impact_downtime": 18.0,
        "units_at_risk": 2100,
        "breakdown_cost": 240000
    },
    "CNV-023": {
        "status": "High",
        "predicted_failure": "Conveyor Motor Overload & Drive Coupling Failure",
        "sensor_overrides": {"rpm": 410.0, "current": 27.8, "vibration": 6.5, "temp": 75.6, "power": 17.8, "load": 95.0},
        "days_overdue": 9,
        "historical_failures": 3,
        "failure_prob": 74.8,
        "health_score": 49.0,
        "risk_level": "High",
        "confidence": 88.5,
        "impact_downtime": 8.0,
        "units_at_risk": 950,
        "breakdown_cost": 115000
    },
    "HYD-017": {
        "status": "High",
        "predicted_failure": "Hydraulic Overheating & Proportional Valve Leak",
        "sensor_overrides": {"pressure": 248.0, "temp": 82.5, "vibration": 5.8, "current": 48.0, "oil_level": 44.0, "load": 91.0},
        "days_overdue": 8,
        "historical_failures": 4,
        "failure_prob": 71.5,
        "health_score": 52.0,
        "risk_level": "High",
        "confidence": 86.0,
        "impact_downtime": 12.0,
        "units_at_risk": 820,
        "breakdown_cost": 165000
    },
    "ROB-008": {
        "status": "High",
        "predicted_failure": "Welding Arm Servo Imbalance & Cable Harness Wear",
        "sensor_overrides": {"current": 184.0, "vibration": 4.85, "temp": 76.2, "voltage": 46.5, "load": 89.0},
        "days_overdue": 6,
        "historical_failures": 2,
        "failure_prob": 68.0,
        "health_score": 55.5,
        "risk_level": "High",
        "confidence": 85.0,
        "impact_downtime": 9.5,
        "units_at_risk": 620,
        "breakdown_cost": 130000
    },
    "IMM-006": {
        "status": "Warning",
        "predicted_failure": "Barrel Heating Element & Cooling Channel Clog",
        "sensor_overrides": {"temp": 241.5, "pressure": 218.0, "current": 66.0, "power": 61.0, "load": 88.0},
        "days_overdue": 3,
        "historical_failures": 2,
        "failure_prob": 58.5,
        "health_score": 62.0,
        "risk_level": "High",
        "confidence": 84.0,
        "impact_downtime": 7.0,
        "units_at_risk": 780,
        "breakdown_cost": 95000
    },
    "LTH-003": {
        "status": "Warning",
        "predicted_failure": "Headstock Spindle Bearing Deterioration",
        "sensor_overrides": {"vibration": 6.2, "temp": 75.8, "oil_level": 42.0, "current": 32.5, "load": 84.0},
        "days_overdue": 4,
        "historical_failures": 2,
        "failure_prob": 53.0,
        "health_score": 64.0,
        "risk_level": "High",
        "confidence": 82.0,
        "impact_downtime": 6.5,
        "units_at_risk": 540,
        "breakdown_cost": 85000
    },
    "MIL-005": {
        "status": "Warning",
        "predicted_failure": "Spindle Imbalance & Lubrication Starvation",
        "sensor_overrides": {"oil_level": 29.5, "vibration": 6.9, "temp": 81.0, "current": 34.0, "load": 86.0},
        "days_overdue": 5,
        "historical_failures": 3,
        "failure_prob": 64.5,
        "health_score": 58.0,
        "risk_level": "High",
        "confidence": 87.0,
        "impact_downtime": 8.5,
        "units_at_risk": 680,
        "breakdown_cost": 110000
    }
}


def generate_all_datasets():
    print(f"Generating comprehensive dataset for {COMPANY_NAME}...")
    machines = []
    machine_lookup = {}
    current_time = datetime(2026, 10, 12, 10, 0, 0)
    
    # 1. GENERATE MACHINE MASTER DATA (Total 105 machines)
    m_idx = 1
    for m_type_info in MACHINE_TYPES:
        prefix = m_type_info["prefix"]
        count = m_type_info["count"]
        m_type_name = m_type_info["type"]
        dept = m_type_info["dept"]
        
        for num in range(1, count + 1):
            m_id = f"{prefix}-{str(num).zfill(3)}"
            m_name = f"{m_type_name} #{num}"
            age_years = round(random.uniform(0.8, 7.5), 1)
            install_date = (current_time - timedelta(days=int(age_years * 365.25))).strftime("%Y-%m-%d")
            warranty_status = "Active" if age_years <= 2.0 else "Expired"
            operating_hours = int(age_years * random.randint(3100, 4800))
            
            mfr = random.choice(m_type_info["mfrs"])
            model = random.choice(m_type_info["models"])
            prod_line = random.choice(PRODUCTION_LINES)
            shift_pattern = random.choice(SHIFT_PATTERNS)
            criticality = random.choices(CRITICALITY_LEVELS, weights=[0.25, 0.35, 0.25, 0.15])[0]
            
            num_previous_failures = random.randint(0, 4)
            downtime_hours = round(num_previous_failures * random.uniform(4.5, 12.0) + random.uniform(1.0, 15.0), 1)
            total_maint_cost = int(num_previous_failures * random.randint(25000, 75000) + random.randint(15000, 85000))
            
            days_since_maint = random.randint(5, 75)
            last_maint_date = (current_time - timedelta(days=days_since_maint)).strftime("%Y-%m-%d")
            
            next_maint_days = random.randint(-15, 45)
            next_maint_date = (current_time + timedelta(days=next_maint_days)).strftime("%Y-%m-%d")
            
            utilization = round(random.uniform(62.0, 94.0), 1)
            
            preset = PRESET_ANOMALIES.get(m_id)
            if preset:
                health_score = preset["health_score"]
                failure_prob = preset["failure_prob"]
                risk_level = preset["risk_level"]
                num_previous_failures = preset["historical_failures"]
                next_maint_date = (current_time - timedelta(days=preset["days_overdue"])).strftime("%Y-%m-%d")
                criticality = "Critical" if risk_level == "Critical" else ("High" if risk_level == "High" else criticality)
                utilization = round(random.uniform(88.0, 96.0), 1)
            else:
                dice = random.random()
                if dice < 0.45:
                    health_score = round(random.uniform(90.0, 98.5), 1)
                    failure_prob = round(random.uniform(2.0, 14.0), 1)
                    risk_level = "Low"
                elif dice < 0.80:
                    health_score = round(random.uniform(75.0, 89.5), 1)
                    failure_prob = round(random.uniform(14.1, 25.0), 1)
                    risk_level = "Low"
                elif dice < 0.94:
                    health_score = round(random.uniform(60.0, 74.5), 1)
                    failure_prob = round(random.uniform(26.0, 48.0), 1)
                    risk_level = "Moderate"
                else:
                    health_score = round(random.uniform(48.0, 59.5), 1)
                    failure_prob = round(random.uniform(51.0, 68.0), 1)
                    risk_level = "High"
            
            machine_record = {
                "Machine_ID": m_id,
                "Machine_Name": m_name,
                "Machine_Type": m_type_name,
                "Department": dept,
                "Installation_Date": install_date,
                "Machine_Age": f"{age_years} yrs",
                "Machine_Age_Years": age_years,
                "Manufacturer": mfr,
                "Model": model,
                "Warranty_Status": warranty_status,
                "Operating_Hours": operating_hours,
                "Maximum_Rated_Capacity": m_type_info["rated_cap"],
                "Current_Utilization": utilization,
                "Production_Line": prod_line["name"],
                "Production_Line_ID": prod_line["id"],
                "Shift_Pattern": shift_pattern,
                "Criticality_Level": criticality,
                "Last_Maintenance_Date": last_maint_date,
                "Next_Scheduled_Maintenance_Date": next_maint_date,
                "Number_of_Previous_Failures": num_previous_failures,
                "Total_Maintenance_Cost": total_maint_cost,
                "Total_Downtime_Hours": downtime_hours,
                "Current_Machine_Health_Score": health_score,
                "Current_Failure_Probability": failure_prob,
                "Current_Risk_Level": risk_level,
                "Sensor_Config": m_type_info["sensors"]
            }
            machines.append(machine_record)
            machine_lookup[m_id] = machine_record
            m_idx += 1
            
    print(f"Created {len(machines)} master machine records for {COMPANY_NAME}.")

    # 2. GENERATE TIME-SERIES SENSOR DATA
    latest_sensors = {}
    time_series_telemetry = {}
    
    history_points = []
    for h in [24, 20, 16, 12, 8, 4, 1, 0]:
        history_points.append(current_time - timedelta(hours=h))
    for d in [2, 3, 4, 5, 6, 7]:
        history_points.append(current_time - timedelta(days=d))
    for d in [10, 14, 18, 22, 26, 30]:
        history_points.append(current_time - timedelta(days=d))
    for d in [40, 50, 60, 70, 80, 90]:
        history_points.append(current_time - timedelta(days=d))
        
    history_points = sorted(list(set(history_points)))
    
    for m in machines:
        m_id = m["Machine_ID"]
        cfg = m["Sensor_Config"]
        preset = PRESET_ANOMALIES.get(m_id)
        m_history = []
        
        for t_idx, dt in enumerate(history_points):
            is_latest = (t_idx == len(history_points) - 1)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
            progress = t_idx / (len(history_points) - 1)
            
            readings = {}
            for s_name, s_range in cfg.items():
                norm_min, norm_max = s_range["normal"]
                base_val = norm_min + (norm_max - norm_min) * 0.5 + random.uniform(-0.1, 0.1) * (norm_max - norm_min)
                
                if preset and s_name in preset["sensor_overrides"]:
                    target_val = preset["sensor_overrides"][s_name]
                    if progress < 0.5:
                        val = base_val + random.uniform(-0.03, 0.03) * base_val
                    else:
                        weight = (progress - 0.5) * 2.0
                        val = base_val * (1.0 - weight) + target_val * weight + random.uniform(-0.015, 0.015) * target_val
                    if is_latest:
                        val = target_val
                elif preset:
                    val = base_val * (1.0 + 0.15 * progress * random.random())
                else:
                    health = m["Current_Machine_Health_Score"]
                    noise_factor = (100.0 - health) / 100.0
                    val = base_val + (random.uniform(-0.08, 0.08) + noise_factor * 0.12) * base_val
                    
                readings[s_name] = round(val, 2)
            
            record = {"timestamp": time_str, "readings": readings}
            m_history.append(record)
            
            if is_latest:
                latest_sensors[m_id] = readings
                
        time_series_telemetry[m_id] = m_history

    # 3. MAINTENANCE HISTORY RECORDS (600+ entries)
    maintenance_records = []
    maint_id_seq = 1001
    
    MAINT_TYPES = [
        "Preventive Maintenance", "Corrective Maintenance", "Breakdown Maintenance",
        "Inspection", "Lubrication", "Calibration", "Component Replacement"
    ]
    FAILURE_TYPES = [
        "Bearing Wear / Spindle Seizure", "Motor Overload & Winding Breakdown",
        "Hydraulic Valve & Seal Leakage", "Compressor Overheating & Cylinder Wear",
        "Cooling Circuit Clogging", "Servo Arm Backlash & Cable Fatigue",
        "Toolholder Runout & Spindle Imbalance", "Drive Belt Slippage & Tension Drop"
    ]
    TECHNICIANS = [
        "Vikram Sengupta (Reliability Lead)", "Anil Rane (Pneumatics)", "Manish Kulkarni (Mechanical)",
        "Suresh Nair (Electrical Lead)", "Karthik Verma (Automation)", "Manoj Desai (Hydraulics)"
    ]
    PARTS_POOL = [
        "SKF Angular Contact Bearings", "Siemens Servomotor Encoder", "Rexroth Directional Valve",
        "Viton Seal Kit", "Mobil DTE 25 Hydraulic Oil (50L)", "Kaeser Air Filter Cartridge",
        "Gates Poly Chain Carbon Belt", "Kuka Wrist Cable Harness", "Omron Proximity Sensors",
        "Fanuc Spindle Sensor Ring", "Spindle Cooling Heat Exchanger"
    ]
    
    for m in machines:
        m_id = m["Machine_ID"]
        num_past = m["Number_of_Previous_Failures"] + random.randint(2, 5)
        
        for k in range(num_past):
            days_ago = random.randint(12, 350)
            m_date = (current_time - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            m_type = random.choices(MAINT_TYPES, weights=[0.45, 0.20, 0.10, 0.10, 0.05, 0.05, 0.05])[0]
            
            is_breakdown = (m_type == "Breakdown Maintenance")
            is_preventive = (m_type in ["Preventive Maintenance", "Inspection", "Lubrication", "Calibration"])
            
            fail_type = random.choice(FAILURE_TYPES) if not is_preventive else "None (Routine PM)"
            prob_desc = "Scheduled autonomous PM and oil filtration" if is_preventive else "Elevated vibration and thermal trip during high-torque machining; replaced assembly"
            parts = [random.choice(PARTS_POOL)] if (is_breakdown or random.random() < 0.4) else ["None (Inspection & Labor)"]
            tech = random.choice(TECHNICIANS)
            cost = random.randint(35000, 110000) if is_breakdown else random.randint(4500, 18500)
            dt_hours = round(random.uniform(6.0, 16.0), 1) if is_breakdown else round(random.uniform(0.5, 3.0), 1)
            
            maintenance_records.append({
                "Maintenance_ID": f"MNT-{maint_id_seq}",
                "Machine_ID": m_id,
                "Machine_Type": m["Machine_Type"],
                "Maintenance_Date": m_date,
                "Maintenance_Type": m_type,
                "Failure_Type": fail_type,
                "Problem_Description": prob_desc,
                "Parts_Replaced": ", ".join(parts),
                "Technician": tech,
                "Maintenance_Cost": cost,
                "Downtime_Hours": dt_hours,
                "Maintenance_Status": "Completed",
                "Was_Preventive": is_preventive,
                "Was_Breakdown": is_breakdown
            })
            maint_id_seq += 1

    # 4. PRODUCTION SCHEDULE
    production_schedules = []
    for m in machines[:50]:
        for day_offset in range(14):
            sched_date = (current_time - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            for shift_name in ["Shift 1 (06:00-14:00)", "Shift 2 (14:00-22:00)", "Shift 3 (22:00-06:00)"]:
                sched_h = 8.0
                util = m["Current_Utilization"]
                actual_h = round(sched_h * (util / 100.0) + random.uniform(-0.4, 0.4), 1)
                target_pcs = random.randint(240, 580)
                actual_pcs = int(target_pcs * (actual_h / sched_h) * random.uniform(0.92, 1.02))
                overtime = round(random.choice([0.0, 0.0, 1.0, 1.5, 2.0]), 1) if util > 85 else 0.0
                
                production_schedules.append({
                    "Machine_ID": m["Machine_ID"],
                    "Date": sched_date,
                    "Shift": shift_name,
                    "Scheduled_Hours": sched_h,
                    "Actual_Operating_Hours": actual_h,
                    "Production_Target": target_pcs,
                    "Actual_Production": actual_pcs,
                    "Production_Load_%": round(min(100.0, util + random.uniform(-3, 5)), 1),
                    "Utilization_%": util,
                    "Overtime_Hours": overtime,
                    "Production_Priority": m["Criticality_Level"]
                })

    # 5. DATA QUALITY METRICS
    total_sensor_records = len(machines) * len(history_points) * 10
    missing_values = 14
    duplicates = 6
    abnormal_sensor_readings = 182
    valid_records = total_sensor_records - missing_values - duplicates
    data_quality_pct = round((valid_records / total_sensor_records) * 100, 2)
    
    data_quality_stats = {
        "Company": COMPANY_NAME,
        "Total_Records": total_sensor_records,
        "Valid_Records": valid_records,
        "Missing_Values": missing_values,
        "Duplicate_Records": duplicates,
        "Abnormal_Sensor_Readings": abnormal_sensor_readings,
        "Data_Quality_Percentage": data_quality_pct,
        "Pipeline_Stages": [
            {"stage": "1. Timestamp Validation", "status": "Passed", "records_validated": total_sensor_records, "errors": 0},
            {"stage": "2. Machine ID Validation", "status": "Passed", "records_validated": total_sensor_records, "errors": 0},
            {"stage": "3. Missing Value Imputation", "status": "Passed", "records_fixed": missing_values, "method": "Forward-Fill + Median"},
            {"stage": "4. Duplicate De-duplication", "status": "Passed", "records_deduped": duplicates, "method": "Primary Key Dedupe"},
            {"stage": "5. Outlier Detection (Z-Score > 3.0)", "status": "Alert", "outliers_flagged": abnormal_sensor_readings, "method": "Adaptive Z-Score & Physics Range"},
            {"stage": "6. Sensor Normalization", "status": "Passed", "records_normalized": total_sensor_records, "method": "MinMax & Standard Scaler"},
            {"stage": "7. Maintenance History Matching", "status": "Passed", "matches": len(maintenance_records), "unmatched": 0},
            {"stage": "8. Production Schedule Synchronization", "status": "Passed", "matches": len(production_schedules), "unmatched": 0}
        ]
    }

    # Save to disk
    with open(os.path.join(DATA_DIR, "machines_master.json"), "w") as f:
        json.dump(machines, f, indent=2)
    with open(os.path.join(DATA_DIR, "latest_sensors.json"), "w") as f:
        json.dump(latest_sensors, f, indent=2)
    with open(os.path.join(DATA_DIR, "telemetry_history.json"), "w") as f:
        json.dump(time_series_telemetry, f, indent=2)
    with open(os.path.join(DATA_DIR, "maintenance_history.json"), "w") as f:
        json.dump(maintenance_records, f, indent=2)
    with open(os.path.join(DATA_DIR, "production_schedule.json"), "w") as f:
        json.dump(production_schedules, f, indent=2)
    with open(os.path.join(DATA_DIR, "data_quality.json"), "w") as f:
        json.dump(data_quality_stats, f, indent=2)
        
    pd.DataFrame(machines).drop(columns=["Sensor_Config"]).to_csv(os.path.join(DATA_DIR, "machines_master.csv"), index=False)
    pd.DataFrame(maintenance_records).to_csv(os.path.join(DATA_DIR, "maintenance_history.csv"), index=False)
    pd.DataFrame(production_schedules).to_csv(os.path.join(DATA_DIR, "production_schedule.csv"), index=False)
    
    print(f"All datasets generated and saved for {COMPANY_NAME} successfully!")


if __name__ == "__main__":
    generate_all_datasets()
