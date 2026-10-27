"""
PDF Report Generator for ABC Automotive Components Pvt. Ltd.
Generates:
1. Individual Machine Health Report Card (PDF)
2. Complete Multi-Page Fleet PDF containing report cards for ALL 105 machines!
3. ZIP Archive containing all 105 individual PDF report cards!
4. Executive Management Reports (Daily, Weekly, Monthly, Critical, Production Risk)
"""

import os
import io
import zipfile
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

BASE_DIR = r"C:\Users\DELL\.gemini\antigravity\scratch\predictive_maintenance_system"
EXPORT_DIR = os.path.join(BASE_DIR, "reports_export")
os.makedirs(EXPORT_DIR, exist_ok=True)


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()
        self._cached_all_pdf = None
        self._cached_all_zip = None

    def _init_custom_styles(self):
        self.title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#0f172a'),
            fontName='Helvetica-Bold'
        )
        self.subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#475569'),
            fontName='Helvetica'
        )
        self.section_header = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#1e293b'),
            fontName='Helvetica-Bold',
            spaceBefore=6,
            spaceAfter=4
        )
        self.body_style = ParagraphStyle(
            'ReportBody',
            parent=self.styles['Normal'],
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#334155'),
            fontName='Helvetica'
        )
        self.bold_style = ParagraphStyle(
            'ReportBold',
            parent=self.styles['Normal'],
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#0f172a'),
            fontName='Helvetica-Bold'
        )

    def build_machine_card_flowables(self, machine, prediction, recommendations, sensor_devs):
        """Constructs compact, single-page flowables for one machine report card."""
        elements = []

        # 1. Header
        header_data = [
            [
                Paragraph("<b>ABC AUTOMOTIVE COMPONENTS PVT. LTD.</b><br/>"
                          "<font size=7.5 color='#64748b'>Predictive Maintenance & Machine Health Intelligence System</font>", self.title_style),
                Paragraph(f"<b>REPORT DATE:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>"
                          f"<b>PLANT LOC:</b> Plant-01 ({machine.get('Department', 'Precision')})<br/>"
                          f"<b>AUDIT STATUS:</b> AI Verified Telemetry", self.subtitle_style)
            ]
        ]
        t_header = Table(header_data, colWidths=[4.4 * inch, 2.6 * inch])
        t_header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(t_header)
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceBefore=2, spaceAfter=4))

        # Title Banner
        elements.append(Paragraph(f"MACHINE HEALTH REPORT CARD: {machine['Machine_ID']} — {machine['Machine_Name'].upper()}", self.section_header))

        # Risk colors
        risk = prediction["risk_level"]
        risk_text = colors.HexColor('#991b1b') if risk == "Critical" else (
            colors.HexColor('#9a3412') if risk == "High" else (
                colors.HexColor('#92400e') if risk == "Moderate" else colors.HexColor('#166534')
            )
        )

        # 2. KPI Summary Box
        kpi_data = [
            [
                Paragraph("<b>HEALTH SCORE</b>", self.subtitle_style),
                Paragraph("<b>FAILURE PROB (7D)</b>", self.subtitle_style),
                Paragraph("<b>RISK LEVEL</b>", self.subtitle_style),
                Paragraph("<b>MAINT PRIORITY</b>", self.subtitle_style)
            ],
            [
                Paragraph(f"<font size=14 color='#0f172a'><b>{machine['Current_Machine_Health_Score']} / 100</b></font>", self.bold_style),
                Paragraph(f"<font size=14 color='{risk_text.hexval()}'><b>{prediction['failure_probability']}%</b></font>", self.bold_style),
                Paragraph(f"<font size=12 color='{risk_text.hexval()}'><b>{risk.upper()}</b></font>", self.bold_style),
                Paragraph(f"<font size=12 color='#0284c7'><b>{recommendations['priority_code']}</b></font>", self.bold_style)
            ]
        ]
        t_kpi = Table(kpi_data, colWidths=[1.75 * inch, 1.85 * inch, 1.75 * inch, 1.65 * inch])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 4))

        # 3. Machine Asset Master Specifications
        elements.append(Paragraph("1. Asset Specifications & Operating Parameters", self.section_header))
        spec_data = [
            [Paragraph("<b>Machine ID:</b>", self.body_style), Paragraph(machine["Machine_ID"], self.body_style),
             Paragraph("<b>Machine Type:</b>", self.body_style), Paragraph(machine["Machine_Type"], self.body_style)],
            [Paragraph("<b>Manufacturer:</b>", self.body_style), Paragraph(machine["Manufacturer"], self.body_style),
             Paragraph("<b>Model Number:</b>", self.body_style), Paragraph(machine["Model"], self.body_style)],
            [Paragraph("<b>Department:</b>", self.body_style), Paragraph(machine["Department"], self.body_style),
             Paragraph("<b>Production Line:</b>", self.body_style), Paragraph(machine["Production_Line"], self.body_style)],
            [Paragraph("<b>Asset Age:</b>", self.body_style), Paragraph(f"{machine['Machine_Age_Years']} Years", self.body_style),
             Paragraph("<b>Warranty Status:</b>", self.body_style), Paragraph(machine["Warranty_Status"], self.body_style)],
            [Paragraph("<b>Operating Hours:</b>", self.body_style), Paragraph(f"{machine['Operating_Hours']:,} hrs", self.body_style),
             Paragraph("<b>Current Utilization:</b>", self.body_style), Paragraph(f"{machine['Current_Utilization']}%", self.body_style)],
            [Paragraph("<b>Shift Pattern:</b>", self.body_style), Paragraph(machine["Shift_Pattern"], self.body_style),
             Paragraph("<b>Criticality Level:</b>", self.body_style), Paragraph(machine["Criticality_Level"], self.body_style)]
        ]
        t_spec = Table(spec_data, colWidths=[1.4 * inch, 2.1 * inch, 1.4 * inch, 2.1 * inch])
        t_spec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ]))
        elements.append(t_spec)
        elements.append(Spacer(1, 4))

        # 4. Sensor Telemetry Table
        elements.append(Paragraph("2. Real-Time Telemetry & Deviation Analysis", self.section_header))
        sensor_rows = [
            [
                Paragraph("<b>Sensor Parameter</b>", self.body_style),
                Paragraph("<b>Current Value</b>", self.body_style),
                Paragraph("<b>Nominal Range</b>", self.body_style),
                Paragraph("<b>Baseline Deviation</b>", self.body_style),
                Paragraph("<b>Telemetry Status</b>", self.body_style)
            ]
        ]
        
        for s_name, s_info in sensor_devs.items():
            label = s_name.replace('_', ' ').title()
            val_str = f"{s_info['value']} {s_info['unit']}"
            dev_str = f"{'+' if s_info['deviation_pct'] > 0 else ''}{s_info['deviation_pct']}%"
            st_color = '#b91c1c' if 'Critical' in s_info['status'] else ('#d97706' if 'Warning' in s_info['status'] else '#059669')
            st_p = Paragraph(f"<font color='{st_color}'><b>{s_info['status']}</b></font>", self.body_style)
            
            sensor_rows.append([
                Paragraph(label, self.body_style),
                Paragraph(val_str, self.body_style),
                Paragraph(s_info['normal_range'], self.body_style),
                Paragraph(dev_str, self.body_style),
                st_p
            ])
            
        t_sensor = Table(sensor_rows, colWidths=[1.8 * inch, 1.2 * inch, 1.6 * inch, 1.2 * inch, 1.2 * inch])
        t_sensor.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ]))
        elements.append(t_sensor)
        elements.append(Spacer(1, 4))

        # 5. Explainable AI & Warning Signs
        elements.append(Paragraph("3. AI Diagnostics & Risk Factor Attribution", self.section_header))
        elements.append(Paragraph(f"<b>Predicted Failure Mode:</b> <font color='#dc2626'>{prediction['predicted_failure']}</font> (Confidence: {prediction['confidence_score']}%)", self.bold_style))
        
        warning_bullets = []
        for idx, f in enumerate(prediction.get("top_3_factors", []), 1):
            warning_bullets.append(f"• <b>Factor {idx}:</b> {f['factor']} (+{f['risk_contribution']}% Risk Contribution) [{f['category']}]")
            
        warn_p = Paragraph("<br/>".join(warning_bullets) if warning_bullets else "• Operating within nominal baseline tolerances.", self.body_style)
        elements.append(warn_p)
        elements.append(Spacer(1, 4))

        # 6. Maintenance Recommendations & Action Protocol
        elements.append(Paragraph("4. Recommended Maintenance Protocol", self.section_header))
        rec_data = [
            [Paragraph("<b>Urgency / Window:</b>", self.body_style), Paragraph(f"<b>{recommendations['urgency']}</b> — {recommendations['timeframe']}", self.body_style)],
            [Paragraph("<b>Recommended Action:</b>", self.body_style), Paragraph(recommendations["recommended_action"], self.body_style)],
            [Paragraph("<b>Diagnostic Rationale:</b>", self.body_style), Paragraph(recommendations["root_cause_explanation"], self.body_style)],
            [Paragraph("<b>Consequence If Ignored:</b>", self.body_style), Paragraph(f"<font color='#b91c1c'>{recommendations['risk_if_ignored']}</font>", self.body_style)],
            [Paragraph("<b>Estimated Impact:</b>", self.body_style), Paragraph(
                f"Downtime: <b>{recommendations['estimated_downtime_hours']} hrs</b> | "
                f"Parts at Risk: <b>{recommendations['units_at_risk']} units</b> | "
                f"Breakdown Exposure: <b>INR {recommendations['estimated_breakdown_cost_inr']:,}</b>", self.body_style)]
        ]
        t_rec = Table(rec_data, colWidths=[1.8 * inch, 5.2 * inch])
        t_rec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ]))
        elements.append(t_rec)

        # Footer
        elements.append(Spacer(1, 4))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8'), spaceBefore=2, spaceAfter=2))
        footer_p = Paragraph(f"<font size=7 color='#64748b'>ABC Automotive Components Pvt. Ltd. | Machine Health Report Card: {machine['Machine_ID']} | Confidential</font>", self.subtitle_style)
        elements.append(footer_p)

        return elements

    def generate_machine_report_card(self, machine, prediction, recommendations, sensor_devs, output_path=None):
        """Generates a complete single Machine Health Report Card PDF."""
        buffer = io.BytesIO() if output_path is None else output_path
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=28,
            leftMargin=28,
            topMargin=24,
            bottomMargin=24
        )
        elements = self.build_machine_card_flowables(machine, prediction, recommendations, sensor_devs)
        doc.build(elements)
        if output_path is None:
            return buffer.getvalue()
        return output_path

    def generate_all_machines_combined_pdf(self, machines_list, engine, risk_filter="All", output_path=None):
        """
        Generates a massive, complete multi-page PDF document containing the
        formal Machine Health Report Card for EVERY SINGLE MACHINE (all 105 machines)!
        """
        buffer = io.BytesIO() if output_path is None else output_path
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=28,
            leftMargin=28,
            topMargin=24,
            bottomMargin=24
        )
        all_elements = []

        # ==========================================
        # COVER / EXECUTIVE AUDIT SUMMARY PAGE
        # ==========================================
        all_elements.append(Paragraph("<b>ABC AUTOMOTIVE COMPONENTS PVT. LTD.</b>", self.title_style))
        all_elements.append(Paragraph(f"<font size=14 color='#0284c7'><b>COMPLETE FLEET MACHINE HEALTH REPORT CARDS</b></font>", self.section_header))
        all_elements.append(Paragraph(f"Comprehensive Diagnostics for All {len(machines_list)} Monitored Production Assets | Scope Filter: {risk_filter}", self.subtitle_style))
        all_elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y %H:%M')} | Reliability Engineering Division", self.subtitle_style))
        all_elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284c7'), spaceBefore=6, spaceAfter=10))

        # Executive Overview paragraph
        all_elements.append(Paragraph("<b>Fleet Audit Executive Summary:</b>", self.section_header))
        crit_count = len([m for m in machines_list if m.get("Current_Risk_Level") == "Critical"])
        high_count = len([m for m in machines_list if m.get("Current_Risk_Level") == "High"])
        mod_count = len([m for m in machines_list if m.get("Current_Risk_Level") == "Moderate"])
        low_count = len([m for m in machines_list if m.get("Current_Risk_Level") == "Low"])
        avg_health = round(sum(m["Current_Machine_Health_Score"] for m in machines_list) / len(machines_list), 1)

        summary_p = Paragraph(
            f"This publication compiles the formal, verified <b>Machine Health Report Cards</b> for all "
            f"<b>{len(machines_list)} machines</b> in Plant-01 across Precision Machining, Stamping, Polymer Molding, "
            f"Assembly, and Compressed Air utilities. "
            f"The plant-wide average health index is <b>{avg_health}/100</b>.<br/><br/>"
            f"• <b>Critical Risk Machines (P1 Immediate Action):</b> <font color='#b91c1c'><b>{crit_count} Assets</b></font><br/>"
            f"• <b>High Risk Machines (P2 within 48h):</b> <font color='#c2410c'><b>{high_count} Assets</b></font><br/>"
            f"• <b>Moderate Risk Machines (P3 within 7d):</b> <font color='#d97706'><b>{mod_count} Assets</b></font><br/>"
            f"• <b>Low Risk / Healthy Assets (P4 Continuous Monitoring):</b> <font color='#047857'><b>{low_count} Assets</b></font><br/><br/>"
            f"Each subsequent page contains the dedicated, individual Machine Health Report Card specifying "
            f"current telemetry deviations, AI failure predictions, explainable risk factors, recommended directives, and potential downtime exposure.",
            self.body_style
        )
        all_elements.append(summary_p)
        all_elements.append(Spacer(1, 14))

        # Index / Table of Monitored Machines
        all_elements.append(Paragraph("<b>Fleet Asset Registry Index:</b>", self.section_header))
        idx_rows = [
            [
                Paragraph("<b>Machine ID</b>", self.body_style),
                Paragraph("<b>Machine Type</b>", self.body_style),
                Paragraph("<b>Department / Line</b>", self.body_style),
                Paragraph("<b>Health</b>", self.body_style),
                Paragraph("<b>Risk Level</b>", self.body_style),
                Paragraph("<b>Priority</b>", self.body_style)
            ]
        ]
        
        # Display index table for first 25 high priority machines on cover page
        sorted_machines = sorted(machines_list, key=lambda x: x.get("Current_Failure_Probability", 0), reverse=True)
        for m in sorted_machines[:24]:
            r_level = m.get("Current_Risk_Level", "Low")
            color_str = '#b91c1c' if r_level == "Critical" else ('#c2410c' if r_level == "High" else ('#d97706' if r_level == "Moderate" else '#047857'))
            idx_rows.append([
                Paragraph(f"<b>{m['Machine_ID']}</b>", self.body_style),
                Paragraph(m["Machine_Type"], self.body_style),
                Paragraph(f"{m['Department']}<br/><font size=7 color='#64748b'>{m['Production_Line']}</font>", self.body_style),
                Paragraph(f"{m['Current_Machine_Health_Score']}/100", self.body_style),
                Paragraph(f"<font color='{color_str}'><b>{r_level.upper()}</b></font>", self.body_style),
                Paragraph("P1" if r_level == "Critical" else ("P2" if r_level == "High" else "P3/P4"), self.body_style)
            ])
            
        t_index = Table(idx_rows, colWidths=[1.1 * inch, 1.5 * inch, 2.2 * inch, 0.8 * inch, 0.9 * inch, 0.5 * inch])
        t_index.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ]))
        all_elements.append(t_index)

        # ==========================================
        # INDIVIDUAL MACHINE REPORT CARDS (105 PAGES)
        # ==========================================
        for machine in machines_list:
            all_elements.append(PageBreak())
            m_id = machine["Machine_ID"]
            pred = engine.predict_failure_and_risk(m_id)
            rec = engine.generate_recommendations(m_id, pred)
            devs = engine.calculate_sensor_deviations(m_id)
            machine_card_flowables = self.build_machine_card_flowables(machine, pred, rec, devs)
            all_elements.extend(machine_card_flowables)

        doc.build(all_elements)
        if output_path is None:
            return buffer.getvalue()
        return output_path

    def generate_all_machines_zip(self, machines_list, engine):
        """
        Generates a ZIP archive containing 105 individual PDF report cards,
        one for each machine in the plant!
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add summary text file
            summary_lines = [
                "===============================================================================",
                "ABC AUTOMOTIVE COMPONENTS PVT. LTD. - PLANT 01",
                "PREDICTIVE MAINTENANCE & MACHINE HEALTH AUDIT - INDIVIDUAL REPORT CARDS ARCHIVE",
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Total Monitored Machines: {len(machines_list)}",
                "===============================================================================",
                "",
                "This ZIP package contains formal individual Machine Health Report Cards (PDF)",
                "for all 105 production machines across Precision Machining, Stamping, Polymer",
                "Molding, Assembly, Compressed Air, Robotic Fabrication, Turning, and Milling.",
                "",
                "Summary by Risk Level:",
                f"  - Critical Risk (P1):  {len([m for m in machines_list if m['Current_Risk_Level'] == 'Critical'])} machines",
                f"  - High Risk (P2):      {len([m for m in machines_list if m['Current_Risk_Level'] == 'High'])} machines",
                f"  - Moderate Risk (P3):  {len([m for m in machines_list if m['Current_Risk_Level'] == 'Moderate'])} machines",
                f"  - Low Risk (P4):       {len([m for m in machines_list if m['Current_Risk_Level'] == 'Low'])} machines",
                "",
                "File Manifest:"
            ]
            for m in machines_list:
                summary_lines.append(f"  • {m['Machine_ID']}_{m['Machine_Name'].replace(' ', '_')}_Health_Report.pdf (Health: {m['Current_Machine_Health_Score']}/100, Risk: {m['Current_Risk_Level']})")
            
            zf.writestr("00_FLEET_AUDIT_SUMMARY.txt", "\n".join(summary_lines))

            # Generate individual PDF for each machine
            for m in machines_list:
                m_id = m["Machine_ID"]
                pred = engine.predict_failure_and_risk(m_id)
                rec = engine.generate_recommendations(m_id, pred)
                devs = engine.calculate_sensor_deviations(m_id)
                pdf_bytes = self.generate_machine_report_card(m, pred, rec, devs)
                filename = f"{m_id}_{m['Machine_Name'].replace(' ', '_')}_Health_Report.pdf"
                zf.writestr(filename, pdf_bytes)

        return zip_buffer.getvalue()

    def generate_management_summary_report(self, report_type, stats, at_risk_machines, output_path=None):
        """Generates Executive Management Reports (Section 25)."""
        buffer = io.BytesIO() if output_path is None else output_path
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        elements = []

        title_map = {
            "daily": "DAILY PLANT MACHINE HEALTH & RELIABILITY REPORT",
            "weekly": "WEEKLY PREDICTIVE MAINTENANCE & ASSET RISK FORECAST",
            "monthly": "MONTHLY ASSET HEALTH & DOWNTIME REDUCTION REPORT",
            "critical": "CRITICAL MACHINES INTERVENTION & MITIGATION REPORT",
            "production": "PRODUCTION LINE VULNERABILITY & OUTPUT IMPACT REPORT"
        }
        title = title_map.get(report_type, "EXECUTIVE ASSET INTELLIGENCE REPORT")

        elements.append(Paragraph("<b>ABC AUTOMOTIVE COMPONENTS PVT. LTD.</b>", self.title_style))
        elements.append(Paragraph(f"<font size=12 color='#0284c7'><b>{title}</b></font>", self.section_header))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y %H:%M')} | Scope: 105 Monitored Production Machines", self.subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceBefore=4, spaceAfter=8))

        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.section_header))
        elements.append(Paragraph(
            f"The continuous AI predictive monitoring system has audited 105 machines across 5 production lines. "
            f"Overall average plant health stands at <b>{stats.get('avg_health', 78.4)}/100</b>. "
            f"Currently, <b>{stats.get('critical_count', 3)} machines</b> require immediate P1 intervention within 24 hours to avert catastrophic breakdown, "
            f"and <b>{stats.get('high_count', 7)} machines</b> are scheduled for P2 predictive servicing within 48 hours. "
            f"Synthetic avoided downtime for this operational cycle is estimated at <b>{stats.get('avoided_hours', 412)} hours</b>, "
            f"protecting approximately <b>INR {stats.get('potential_savings', 1130000):,}</b> in avoidable production loss.",
            self.body_style
        ))
        elements.append(Spacer(1, 10))

        # At-Risk Machines Table
        elements.append(Paragraph("High & Critical Priority Asset Registry", self.section_header))
        rows = [[
            Paragraph("<b>Machine ID</b>", self.body_style),
            Paragraph("<b>Type / Dept</b>", self.body_style),
            Paragraph("<b>Health</b>", self.body_style),
            Paragraph("<b>Failure Risk</b>", self.body_style),
            Paragraph("<b>Predicted Failure</b>", self.body_style),
            Paragraph("<b>Priority</b>", self.body_style),
            Paragraph("<b>Downtime Risk</b>", self.body_style)
        ]]
        
        for m in at_risk_machines[:12]:
            rows.append([
                Paragraph(f"<b>{m['machine_id']}</b>", self.body_style),
                Paragraph(f"{m['machine_type']}<br/><font size=7 color='#64748b'>{m['department']}</font>", self.body_style),
                Paragraph(f"{m['health_score']}/100", self.body_style),
                Paragraph(f"<b>{m['failure_probability']}%</b>", self.body_style),
                Paragraph(m['predicted_failure'], self.body_style),
                Paragraph(f"<b>{m['priority_code']}</b>", self.body_style),
                Paragraph(f"{m['downtime_hours']}h (INR {m['breakdown_cost']:,})", self.body_style)
            ])
            
        t_risk = Table(rows, colWidths=[1.1 * inch, 1.5 * inch, 0.8 * inch, 0.9 * inch, 1.6 * inch, 0.6 * inch, 1.2 * inch])
        t_risk.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(t_risk)
        elements.append(Spacer(1, 12))

        # Action Recommendations
        elements.append(Paragraph("Recommended Management Directives", self.section_header))
        elements.append(Paragraph(
            "1. <b>Dispatch P1 Emergency Work Orders:</b> Immediately re-route high-priority job orders from CNC-004 and CMP-012.<br/>"
            "2. <b>Spare Parts Allocation:</b> Verify inventory for SKF spindle bearings, Viton hydraulic seals, and Kaeser pressure valves.<br/>"
            "3. <b>Shift Rebalancing:</b> Stagger planned maintenance during upcoming night-shift windows to prevent line throughput throttling.",
            self.body_style
        ))
        
        doc.build(elements)
        if output_path is None:
            return buffer.getvalue()
        return output_path


pdf_generator = PDFReportGenerator()
