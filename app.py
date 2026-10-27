"""
FastAPI Backend Application for ABC Automotive Components Pvt. Ltd.
Predictive Maintenance & Machine Health Intelligence System.

Serves RESTful APIs and Static Web Application.
"""

import os
import json
import io
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Query, HTTPException, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ml_engine import engine
from pdf_generator import pdf_generator

BASE_DIR = r"C:\Users\DELL\.gemini\antigravity\scratch\predictive_maintenance_system"
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
EXPORT_DIR = os.path.join(BASE_DIR, "reports_export")

app = FastAPI(
    title="Predictive Maintenance & Machine Health Intelligence System",
    description="AI-powered predictive maintenance platform for ABC Automotive Components Pvt. Ltd.",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory alert state
ACTIVE_ALERTS = []

def init_alerts():
    global ACTIVE_ALERTS
    ACTIVE_ALERTS = []
    # Generate realistic alerts for high/critical machines
    queue = engine.get_maintenance_prioritization_queue()
    seq = 101
    
    for item in queue:
        if item["risk_level"] in ["Critical", "High"]:
            severity = "CRITICAL" if item["risk_level"] == "Critical" else "HIGH"
            badge = "🔴" if severity == "CRITICAL" else "🟠"
            devs = engine.calculate_sensor_deviations(item["machine_id"])
            abnormal_sensors = [s.replace('_', ' ').title() for s, info in devs.items() if info["status"] != "Normal"]
            sensor_str = " + ".join(abnormal_sensors[:3]) if abnormal_sensors else "Multiple telemetry deviations"
            
            ACTIVE_ALERTS.append({
                "alert_id": f"ALT-{seq}",
                "machine_id": item["machine_id"],
                "machine_name": item["machine_name"],
                "machine_type": item["machine_type"],
                "severity": severity,
                "badge": badge,
                "title": f"{severity}: {item['machine_id']} ({item['predicted_failure']})",
                "message": f"Failure probability increased to {item['failure_probability']}%. Detected abnormal pattern: {sensor_str}.",
                "recommended_action": item["recommended_action"],
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(5, 180))).strftime("%Y-%m-%d %H:%M"),
                "status": "Active",
                "priority_code": item["priority_code"]
            })
            seq += 1

init_alerts()


# ==========================================
# 1. MAIN DASHBOARD API
# ==========================================

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """Returns top KPI cards and data for 12 interactive charts."""
    machines = engine.machines
    total_machines = len(machines)
    
    # Health and Risk categories
    health_dist = {"Excellent": 0, "Good": 0, "Warning": 0, "Poor": 0, "Critical": 0}
    risk_dist = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
    
    total_health = 0.0
    critical_count = 0
    at_risk_count = 0
    healthy_count = 0
    predicted_failures_7d = 0
    preventive_due_count = 0
    
    curr_date = datetime(2026, 10, 7)
    
    for m in machines:
        h = m["Current_Machine_Health_Score"]
        total_health += h
        r = m["Current_Risk_Level"]
        
        # Health bucket
        if h >= 90:
            health_dist["Excellent"] += 1
            healthy_count += 1
        elif h >= 75:
            health_dist["Good"] += 1
            healthy_count += 1
        elif h >= 60:
            health_dist["Warning"] += 1
            at_risk_count += 1
        elif h >= 40:
            health_dist["Poor"] += 1
            at_risk_count += 1
        else:
            health_dist["Critical"] += 1
            at_risk_count += 1
            critical_count += 1
            
        # Risk bucket
        if r in risk_dist:
            risk_dist[r] += 1
            
        if r in ["High", "Critical"]:
            predicted_failures_7d += 1
            
        # Maintenance due check
        try:
            nxt = datetime.strptime(m["Next_Scheduled_Maintenance_Date"], "%Y-%m-%d")
            if (nxt - curr_date).days <= 7:
                preventive_due_count += 1
        except Exception:
            pass

    avg_health = round(total_health / total_machines, 1)
    
    # Maintenance and Downtime sums
    total_maint_cost = sum(m["Total_Maintenance_Cost"] for m in machines)
    total_downtime = round(sum(m["Total_Downtime_Hours"] for m in machines), 1)
    
    # 12 CHARTS DATASETS
    
    # 3 & 4. Monthly Health and Failure Risk Trend (Last 6 Months)
    months = ["May", "Jun", "Jul", "Aug", "Sep", "Oct"]
    health_trend = [
        {"month": "May", "avg_health": 82.5, "failure_risk_avg": 16.2},
        {"month": "Jun", "avg_health": 81.8, "failure_risk_avg": 17.5},
        {"month": "Jul", "avg_health": 80.2, "failure_risk_avg": 19.8},
        {"month": "Aug", "avg_health": 79.5, "failure_risk_avg": 21.0},
        {"month": "Sep", "avg_health": 78.9, "failure_risk_avg": 22.4},
        {"month": "Oct (Current)", "avg_health": avg_health, "failure_risk_avg": 23.8}
    ]
    
    # 5, 6, 7, 8. Sensor Trends (CNC-004 vs Fleet Average over recent days)
    sensor_trends = []
    # Sample last 7 days points
    for i in range(7, -1, -1):
        dt = (curr_date - timedelta(days=i)).strftime("%b %d")
        ratio = (7 - i) / 7.0
        sensor_trends.append({
            "date": dt,
            "temp_cnc004": round(65.0 + 23.4 * ratio + random.uniform(-0.8, 0.8), 1),
            "temp_fleet_avg": round(62.0 + random.uniform(-1.0, 1.0), 1),
            "vib_cnc004": round(2.8 + 5.0 * ratio + random.uniform(-0.15, 0.15), 2),
            "vib_fleet_avg": round(2.4 + random.uniform(-0.1, 0.1), 2),
            "rpm_cnc004": round(4600 + 250 * ratio + random.uniform(-50, 50), 0),
            "power_cnc004": round(14.0 + 13.5 * ratio + random.uniform(-0.5, 0.5), 1),
            "oil_cnc004": round(85.0 - 53.0 * ratio + random.uniform(-1.0, 1.0), 1)
        })
        
    # 9 & 10. Maintenance Cost & Downtime Trend
    maint_monthly = [
        {"month": "May", "preventive_cost": 58000, "breakdown_cost": 210000, "downtime_hours": 32.5},
        {"month": "Jun", "preventive_cost": 64000, "breakdown_cost": 185000, "downtime_hours": 28.0},
        {"month": "Jul", "preventive_cost": 72000, "breakdown_cost": 140000, "downtime_hours": 22.5},
        {"month": "Aug", "preventive_cost": 79000, "breakdown_cost": 115000, "downtime_hours": 18.0},
        {"month": "Sep", "preventive_cost": 84000, "breakdown_cost": 92000, "downtime_hours": 14.2},
        {"month": "Oct", "preventive_cost": 68000, "breakdown_cost": 65000, "downtime_hours": 9.5}
    ]
    
    # 11. Production Load vs Failure Risk (Correlation Buckets)
    load_risk_correlation = [
        {"load_bracket": "50-60%", "avg_failure_risk": 8.5, "machine_count": 18},
        {"load_bracket": "60-70%", "avg_failure_risk": 14.2, "machine_count": 28},
        {"load_bracket": "70-80%", "avg_failure_risk": 21.6, "machine_count": 34},
        {"load_bracket": "80-90%", "avg_failure_risk": 44.8, "machine_count": 17},
        {"load_bracket": ">90% (High Load)", "avg_failure_risk": 74.3, "machine_count": 8}
    ]
    
    # 12. Machine Age vs Failure Risk (Correlation Buckets)
    age_risk_correlation = [
        {"age_bracket": "< 2 Years (Under Warranty)", "avg_failure_risk": 9.8, "avg_health": 88.5},
        {"age_bracket": "2 - 4 Years", "avg_failure_risk": 18.2, "avg_health": 81.2},
        {"age_bracket": "4 - 6 Years", "avg_failure_risk": 32.5, "avg_health": 72.8},
        {"age_bracket": "> 6 Years (Legacy Fleet)", "avg_failure_risk": 58.4, "avg_health": 61.4}
    ]
    
    # Top 10 At-Risk Machines
    priority_queue = engine.get_maintenance_prioritization_queue()
    top_10_at_risk = priority_queue[:10]
    
    return {
        "kpis": {
            "total_machines": total_machines,
            "healthy_machines": healthy_count,
            "at_risk_machines": at_risk_count,
            "critical_machines": critical_count,
            "avg_machine_health": avg_health,
            "predicted_failures_7d": predicted_failures_7d,
            "preventive_actions_due": preventive_due_count,
            "total_downtime_hours": total_downtime,
            "total_maintenance_cost_inr": total_maint_cost,
            "plant_availability_pct": round(100.0 - (total_downtime / (total_machines * 365 * 24 / 12)) * 100, 2)
        },
        "charts": {
            "health_distribution": health_dist,
            "risk_distribution": risk_dist,
            "health_trend": health_trend,
            "sensor_trends": sensor_trends,
            "maintenance_monthly": maint_monthly,
            "load_vs_risk": load_risk_correlation,
            "age_vs_risk": age_risk_correlation
        },
        "top_10_at_risk": top_10_at_risk,
        "maintenance_breakdown_stats": {
            "preventive_count": 348,
            "breakdown_count": 68,
            "corrective_count": 114,
            "inspection_count": 76,
            "preventive_spend_inr": 820000,
            "breakdown_spend_inr": 1850000
        }
    }


# ==========================================
# 2. MACHINES LIST & FILTERING API
# ==========================================

@app.get("/api/machines")
def get_machines(
    search: Optional[str] = None,
    machine_type: Optional[str] = None,
    department: Optional[str] = None,
    risk_level: Optional[str] = None,
    health_status: Optional[str] = None,
    production_line: Optional[str] = None,
    criticality: Optional[str] = None
):
    """Returns filtered and searched machines list from the 105 machines dataset."""
    results = []
    
    for m in engine.machines:
        m_id = m["Machine_ID"]
        h = m["Current_Machine_Health_Score"]
        r = m["Current_Risk_Level"]
        
        # Health status category
        h_cat = "Excellent" if h >= 90 else ("Good" if h >= 75 else ("Warning" if h >= 60 else ("Poor" if h >= 40 else "Critical")))
        
        # Filters
        if search:
            s_lower = search.lower()
            match = (
                s_lower in m_id.lower() or
                s_lower in m["Machine_Name"].lower() or
                s_lower in m["Machine_Type"].lower() or
                s_lower in m["Department"].lower() or
                s_lower in m["Model"].lower() or
                s_lower in m["Manufacturer"].lower()
            )
            if not match:
                continue
                
        if machine_type and machine_type != "All" and m["Machine_Type"] != machine_type:
            continue
        if department and department != "All" and m["Department"] != department:
            continue
        if risk_level and risk_level != "All" and r != risk_level:
            continue
        if health_status and health_status != "All" and h_cat != health_status:
            continue
        if production_line and production_line != "All" and m["Production_Line"] != production_line:
            continue
        if criticality and criticality != "All" and m["Criticality_Level"] != criticality:
            continue
            
        pred = engine.predict_failure_and_risk(m_id)
        results.append({
            "Machine_ID": m_id,
            "Machine_Name": m["Machine_Name"],
            "Machine_Type": m["Machine_Type"],
            "Department": m["Department"],
            "Manufacturer": m["Manufacturer"],
            "Model": m["Model"],
            "Machine_Age": m["Machine_Age"],
            "Warranty_Status": m["Warranty_Status"],
            "Operating_Hours": m["Operating_Hours"],
            "Current_Utilization": m["Current_Utilization"],
            "Production_Line": m["Production_Line"],
            "Criticality_Level": m["Criticality_Level"],
            "Last_Maintenance_Date": m["Last_Maintenance_Date"],
            "Next_Scheduled_Maintenance_Date": m["Next_Scheduled_Maintenance_Date"],
            "Health_Score": h,
            "Health_Category": h_cat,
            "Failure_Probability": pred["failure_probability"],
            "Risk_Level": r,
            "Predicted_Failure": pred["predicted_failure"]
        })
        
    return {"total_count": len(results), "machines": results}


# ==========================================
# 3. INDIVIDUAL MACHINE PROFILE & XAI API
# ==========================================

@app.get("/api/machines/{machine_id}")
def get_machine_details(machine_id: str):
    """Detailed machine profile, sensor status cards, XAI factor decomposition, recommendations."""
    machine = next((m for m in engine.machines if m["Machine_ID"] == machine_id), None)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")
        
    sensor_devs = engine.calculate_sensor_deviations(machine_id)
    health, health_cat = engine.calculate_health_score(machine_id)
    pred = engine.predict_failure_and_risk(machine_id)
    rec = engine.generate_recommendations(machine_id, pred)
    
    # Machine-specific maintenance history (latest 8 entries)
    maint_records = [
        rec for rec in engine.maintenance_history if rec["Machine_ID"] == machine_id
    ][:8]
    
    # Machine-specific recent schedule entries
    sched_records = [
        s for s in engine.production_schedules if s["Machine_ID"] == machine_id
    ][:6]
    
    return {
        "machine_master": machine,
        "health_score": health,
        "health_category": health_cat,
        "prediction": pred,
        "recommendations": rec,
        "sensor_deviations": sensor_devs,
        "recent_maintenance": maint_records,
        "recent_schedule": sched_records
    }


# ==========================================
# 4. TIME-SERIES TELEMETRY API (Section 12)
# ==========================================

@app.get("/api/machines/{machine_id}/telemetry")
def get_machine_telemetry(machine_id: str, range_period: str = "30d"):
    """
    Returns time-series telemetry data for charts with normal range, warning & critical thresholds.
    range_period: '24h', '7d', '30d', '90d'
    """
    machine = next((m for m in engine.machines if m["Machine_ID"] == machine_id), None)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
        
    history = engine.telemetry.get(machine_id, [])
    
    # Filter based on range_period
    # Total points are 26
    if range_period == "24h":
        filtered = history[-8:]
    elif range_period == "7d":
        filtered = history[-14:]
    elif range_period == "30d":
        filtered = history[-20:]
    else: # 90d
        filtered = history
        
    cfg = machine["Sensor_Config"]
    
    return {
        "machine_id": machine_id,
        "range_period": range_period,
        "sensor_configs": cfg,
        "telemetry_points": filtered
    }


# ==========================================
# 5. MACHINE HEALTH REPORT CARD & PDF DOWNLOAD
# ==========================================

@app.get("/api/machines/{machine_id}/report-card")
def get_machine_report_card_data(machine_id: str):
    """Returns structured data for the Automated Machine Report Card (Section 13 & 27)."""
    machine = next((m for m in engine.machines if m["Machine_ID"] == machine_id), None)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
        
    sensor_devs = engine.calculate_sensor_deviations(machine_id)
    pred = engine.predict_failure_and_risk(machine_id)
    rec = engine.generate_recommendations(machine_id, pred)
    
    # Key warning signs
    warning_signs = []
    for s_name, s_info in sensor_devs.items():
        if s_info["status"] != "Normal":
            direction = "increased" if s_info["deviation_pct"] > 0 else "decreased"
            warning_signs.append({
                "sensor": s_name.replace('_', ' ').title(),
                "text": f"{s_name.replace('_', ' ').title()} {direction} by {abs(s_info['deviation_pct'])}% ({s_info['value']} {s_info['unit']})",
                "severity": s_info["status"]
            })
            
    return {
        "company_name": "ABC Automotive Components Pvt. Ltd.",
        "project_title": "Machine Health Report Card",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "machine": machine,
        "health_score": machine["Current_Machine_Health_Score"],
        "failure_probability": pred["failure_probability"],
        "risk_level": pred["risk_level"],
        "predicted_failure": pred["predicted_failure"],
        "confidence_score": pred["confidence_score"],
        "sensor_status": sensor_devs,
        "key_warning_signs": warning_signs,
        "ai_recommendations": rec,
        "potential_impact": {
            "estimated_downtime_hours": rec["estimated_downtime_hours"],
            "units_at_risk": rec["units_at_risk"],
            "estimated_breakdown_cost_inr": rec["estimated_breakdown_cost_inr"]
        }
    }

@app.get("/api/machines/{machine_id}/pdf")
def download_machine_pdf(machine_id: str):
    """Generates and streams high-definition ReportLab PDF Report Card for machine."""
    machine = next((m for m in engine.machines if m["Machine_ID"] == machine_id), None)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
        
    sensor_devs = engine.calculate_sensor_deviations(machine_id)
    pred = engine.predict_failure_and_risk(machine_id)
    rec = engine.generate_recommendations(machine_id, pred)
    
    pdf_bytes = pdf_generator.generate_machine_report_card(machine, pred, rec, sensor_devs)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={machine_id}_Health_Report_Card.pdf"}
    )


# ==========================================
# 6. BULK REPORT GENERATION API (Section 14)
# ==========================================

@app.get("/api/reports/bulk-pdf")
@app.get("/api/reports/all-machines-pdf")
def generate_bulk_reports(risk_level: Optional[str] = "All"):
    """
    Generates a complete multi-page PDF document containing the formal
    Machine Health Report Card for EVERY SINGLE MACHINE (all 105 machines)!
    """
    machines_to_include = engine.machines
    if risk_level and risk_level != "All":
        machines_to_include = [m for m in engine.machines if m["Current_Risk_Level"] == risk_level]
        
    pdf_bytes = pdf_generator.generate_all_machines_combined_pdf(machines_to_include, engine, risk_filter=risk_level)
    
    filename = f"ABC_Automotive_All_{len(machines_to_include)}_Machine_Report_Cards_{risk_level}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/reports/all-machines-zip")
def generate_all_machines_zip_archive(risk_level: Optional[str] = "All"):
    """
    Generates a ZIP archive containing individual PDF report cards for
    EVERY SINGLE MACHINE (all 105 separate PDF files).
    """
    machines_to_include = engine.machines
    if risk_level and risk_level != "All":
        machines_to_include = [m for m in engine.machines if m["Current_Risk_Level"] == risk_level]
        
    zip_bytes = pdf_generator.generate_all_machines_zip(machines_to_include, engine)
    
    filename = f"ABC_Automotive_All_{len(machines_to_include)}_Machine_Reports_Archive.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==========================================
# 7. MANAGEMENT REPORTS API (Section 25)
# ==========================================

@app.get("/api/reports/management/{report_type}/pdf")
def download_management_report(report_type: str):
    """Generates Daily, Weekly, Monthly, Critical, or Production management PDF report."""
    priority_queue = engine.get_maintenance_prioritization_queue()
    stats = {
        "avg_health": 78.4,
        "critical_count": 3,
        "high_count": 7,
        "avoided_hours": 412.5,
        "potential_savings": 1130000
    }
    pdf_bytes = pdf_generator.generate_management_summary_report(report_type, stats, priority_queue)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ABC_Automotive_{report_type}_Report.pdf"}
    )


# ==========================================
# 8. ALERT SYSTEM API (Section 15)
# ==========================================

@app.get("/api/alerts")
def get_alerts():
    """Returns active automated alerts."""
    return {"alerts": ACTIVE_ALERTS, "count": len(ACTIVE_ALERTS)}

@app.post("/api/alerts/acknowledge/{alert_id}")
def acknowledge_alert(alert_id: str):
    """Acknowledges an alert in the system."""
    global ACTIVE_ALERTS
    for a in ACTIVE_ALERTS:
        if a["alert_id"] == alert_id:
            a["status"] = "Acknowledged"
            return {"status": "success", "alert": a}
    raise HTTPException(status_code=404, detail="Alert not found")


# ==========================================
# 9. MAINTENANCE PLANNER API (Section 17)
# ==========================================

@app.get("/api/maintenance/schedule")
def get_maintenance_schedule(period: str = "all"):
    """
    Returns maintenance planner schedule with categories:
    Today's maintenance, Upcoming (next 7d, next 30d), Overdue, Critical.
    """
    curr_date = datetime(2026, 10, 7)
    today_items = []
    next_7d_items = []
    next_30d_items = []
    overdue_items = []
    
    queue = engine.get_maintenance_prioritization_queue()
    
    for item in queue:
        m = next(x for x in engine.machines if x["Machine_ID"] == item["machine_id"])
        try:
            nxt_dt = datetime.strptime(m["Next_Scheduled_Maintenance_Date"], "%Y-%m-%d")
            diff = (nxt_dt - curr_date).days
            
            entry = {
                "machine_id": item["machine_id"],
                "machine_name": item["machine_name"],
                "machine_type": item["machine_type"],
                "department": item["department"],
                "scheduled_date": m["Next_Scheduled_Maintenance_Date"],
                "days_diff": diff,
                "priority_code": item["priority_code"],
                "urgency": item["urgency"],
                "predicted_failure": item["predicted_failure"],
                "recommended_action": item["recommended_action"],
                "estimated_duration_hours": round(item["downtime_hours"] * 0.4 + 1.5, 1),
                "estimated_cost_inr": int(item["breakdown_cost"] * 0.25),
                "risk_level": item["risk_level"]
            }
            
            if diff < 0:
                overdue_items.append(entry)
            elif diff == 0:
                today_items.append(entry)
            elif diff <= 7:
                next_7d_items.append(entry)
            else:
                next_30d_items.append(entry)
        except Exception:
            pass

    return {
        "today": today_items,
        "next_7_days": next_7d_items,
        "next_30_days": next_30d_items,
        "overdue": overdue_items,
        "counts": {
            "today": len(today_items),
            "next_7_days": len(next_7d_items),
            "next_30_days": len(next_30d_items),
            "overdue": len(overdue_items)
        }
    }


# ==========================================
# 10. PRODUCTION IMPACT & COST SAVINGS APIs
# ==========================================

@app.get("/api/production-impact")
def get_production_impact():
    """Returns production line impact analysis (Section 16)."""
    summary = engine.get_production_impact_summary()
    queue = engine.get_maintenance_prioritization_queue()
    return {
        "lines_summary": summary,
        "highest_risk_machines": queue[:8],
        "total_units_at_risk": sum(x["total_units_at_risk"] for x in summary),
        "total_potential_loss_inr": sum(x["potential_financial_loss_inr"] for x in summary),
        "total_downtime_hours": round(sum(x["potential_downtime_hours"] for x in summary), 1)
    }

@app.get("/api/cost-savings")
def get_cost_savings():
    """Returns synthetic ROI and cost savings analysis (Section 18)."""
    return engine.get_cost_savings_roi()


# ==========================================
# 11. DATA QUALITY PIPELINE API (Section 24)
# ==========================================

@app.get("/api/data-quality")
def get_data_quality():
    """Returns data quality pipeline audit metrics (Section 24)."""
    with open(os.path.join(DATA_DIR, "data_quality.json"), "r") as f:
        stats = json.load(f)
    return stats


# ==========================================
# 12. WHAT-IF SIMULATION API (Section 20)
# ==========================================

class WhatIfRequest(BaseModel):
    machine_id: str
    temperature: Optional[float] = None
    rpm: Optional[float] = None
    vibration: Optional[float] = None
    pressure: Optional[float] = None
    oil_level: Optional[float] = None
    current: Optional[float] = None
    production_load: Optional[float] = None
    utilization: Optional[float] = None
    days_since_maint: Optional[int] = None

@app.post("/api/what-if")
def calculate_what_if(req: WhatIfRequest):
    """
    Recalculates Health Score, Failure Probability, Risk Level,
    and Recommendations based on user-modified parameters.
    """
    m_id = req.machine_id
    machine = next((m for m in engine.machines if m["Machine_ID"] == m_id), None)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
        
    base_sensors = dict(engine.latest_sensors.get(m_id, {}))
    if req.temperature is not None:
        base_sensors["temp"] = req.temperature
    if req.rpm is not None:
        base_sensors["rpm"] = req.rpm
    if req.vibration is not None:
        base_sensors["vibration"] = req.vibration
    if req.pressure is not None:
        base_sensors["pressure"] = req.pressure
    if req.oil_level is not None:
        base_sensors["oil_level"] = req.oil_level
    if req.current is not None:
        base_sensors["current"] = req.current
    if req.production_load is not None:
        base_sensors["load"] = req.production_load
        
    custom_params = {}
    if req.utilization is not None:
        custom_params["utilization"] = req.utilization
    if req.days_since_maint is not None:
        custom_params["days_since_maint"] = req.days_since_maint
        
    # Recalculate
    new_health, new_h_cat = engine.calculate_health_score(m_id, base_sensors, custom_params)
    new_pred = engine.predict_failure_and_risk(m_id, base_sensors, custom_params)
    new_rec = engine.generate_recommendations(m_id, new_pred)
    new_devs = engine.calculate_sensor_deviations(m_id, base_sensors)
    
    # Compare with current
    curr_health = machine["Current_Machine_Health_Score"]
    curr_prob = machine["Current_Failure_Probability"]
    
    return {
        "machine_id": m_id,
        "baseline": {
            "health_score": curr_health,
            "failure_probability": curr_prob,
            "risk_level": machine["Current_Risk_Level"]
        },
        "simulation_result": {
            "health_score": new_health,
            "health_category": new_h_cat,
            "failure_probability": new_pred["failure_probability"],
            "risk_level": new_pred["risk_level"],
            "predicted_failure": new_pred["predicted_failure"],
            "confidence_score": new_pred["confidence_score"],
            "delta_health": round(new_health - curr_health, 1),
            "delta_probability": round(new_pred["failure_probability"] - curr_prob, 1),
            "recommendation": new_rec,
            "sensor_deviations": new_devs
        }
    }


# ==========================================
# 13. DEMO MODE & LIVE TICK API (Section 29 & 30)
# ==========================================

DEMO_SCENARIO_MAP = {
    "healthy": "CNC-001",
    "warning": "LTH-003",
    "high_risk": "CNV-023",
    "critical": "CNC-004",
    "imminent_failure": "CMP-012"
}

@app.get("/api/demo/scenario/{scenario_name}")
def get_demo_scenario(scenario_name: str):
    """Loads one of the 5 predefined demo scenarios."""
    m_id = DEMO_SCENARIO_MAP.get(scenario_name.lower())
    if not m_id:
        raise HTTPException(status_code=400, detail="Invalid scenario name")
    return get_machine_details(m_id)

@app.post("/api/telemetry/simulate-tick")
def simulate_telemetry_tick():
    """Simulates live arrival of new IoT sensor readings with continuous anomaly detection."""
    for m in engine.machines:
        m_id = m["Machine_ID"]
        cfg = m["Sensor_Config"]
        curr = engine.latest_sensors.get(m_id, {})
        
        # Add slight natural drift
        for s_key in curr:
            drift = np.random.normal(0, 0.015) * curr[s_key]
            curr[s_key] = round(max(0.0, curr[s_key] + drift), 2)
            
    return {"status": "telemetry_updated", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# Mount static directory for frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    """Serves the main application SPA HTML."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

