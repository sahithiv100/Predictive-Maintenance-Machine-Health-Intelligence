/**
 * Predictive Maintenance & Machine Health Intelligence System
 * Client-Side Application Core (SPA, Chart.js Integrations, Diagnostics, APIs)
 * ABC Automotive Components Pvt. Ltd.
 */

// Application State
let currentMachineId = "CNC-004";
let currentModalMachineId = "CNC-004";
let allMachinesData = [];
let dashboardData = null;
let charts = {};
let liveStreamInterval = null;
let isLiveStreaming = false;

// DOM Ready initialization
document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  setupNavigation();
  setupGlobalEvents();
  await loadDashboardData();
  await loadMachinesList();
  await loadAlerts();
  await loadMaintenancePlanner();
  await loadProductionImpact();
  await loadDataQuality();
  loadWhatIfMachine(currentMachineId);
  switchSensorAnalyticsMachine(currentMachineId);
  viewMachineProfile(currentMachineId);
}

// ==========================================
// NAVIGATION & ROUTING
// ==========================================
function setupNavigation() {
  const hash = window.location.hash.replace("#", "") || "dashboard";
  navigateTo(hash);

  window.addEventListener("hashchange", () => {
    const target = window.location.hash.replace("#", "") || "dashboard";
    navigateTo(target);
  });

  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("hidden");
    });
  }
}

function navigateTo(viewId) {
  const views = [
    "dashboard", "machines", "machine-details", "sensor-analytics",
    "predictive-maint", "planner", "alerts", "production-impact",
    "cost-savings", "what-if", "report-cards", "management-reports", "data-quality"
  ];

  views.forEach(v => {
    const el = document.getElementById(`view-${v}`);
    const nav = document.getElementById(`nav-${v}`);
    if (el) {
      if (v === viewId) {
        el.classList.remove("hidden");
      } else {
        el.classList.add("hidden");
      }
    }
    if (nav) {
      if (v === viewId) {
        nav.classList.add("nav-active");
      } else {
        nav.classList.remove("nav-active");
      }
    }
  });

  // Re-render chart layouts if view is dashboard or profile or sensor-analytics
  if (viewId === "dashboard") {
    setTimeout(renderDashboardCharts, 50);
  } else if (viewId === "machine-details") {
    setTimeout(() => loadMachineTelemetryChart("30d"), 50);
  } else if (viewId === "sensor-analytics") {
    setTimeout(renderSensorAnalyticsCharts, 50);
  } else if (viewId === "report-cards") {
    renderReportCardsGrid();
  }
}

// ==========================================
// GLOBAL EVENTS & CONTROLS
// ==========================================
function setupGlobalEvents() {
  // Global search input
  const searchInput = document.getElementById("globalSearchInput");
  if (searchInput) {
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        const val = searchInput.value.trim();
        if (val) {
          navigateTo("machines");
          const mSearch = document.getElementById("filterMachineType");
          filterMachines();
        }
      }
    });
  }

  // Demo scenario dropdown
  const demoSelect = document.getElementById("demoScenarioSelect");
  if (demoSelect) {
    demoSelect.addEventListener("change", async (e) => {
      const scenario = e.target.value;
      if (scenario) {
        await loadDemoScenario(scenario);
      }
    });
  }

  // Live Stream toggle
  const liveToggle = document.getElementById("toggleLiveStreamBtn");
  if (liveToggle) {
    liveToggle.addEventListener("click", () => {
      isLiveStreaming = !isLiveStreaming;
      if (isLiveStreaming) {
        liveToggle.classList.add("bg-emerald-950", "border-emerald-500");
        liveToggle.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span><span class="hidden md:inline text-emerald-300 font-bold">Streaming (2s)</span>`;
        liveStreamInterval = setInterval(simulateLiveTelemetryTick, 2000);
      } else {
        clearInterval(liveStreamInterval);
        liveToggle.classList.remove("bg-emerald-950", "border-emerald-500");
        liveToggle.innerHTML = `<span class="w-2 h-2 rounded-full bg-gray-500"></span><span class="hidden md:inline">Live IoT</span>`;
      }
    });
  }

  // Machines filters events
  ["filterMachineType", "filterRiskLevel", "filterHealthStatus", "filterProductionLine", "filterCriticality"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", filterMachines);
  });
}

// ==========================================
// 1. DASHBOARD & KPIS
// ==========================================
async function loadDashboardData() {
  try {
    const res = await fetch("/api/dashboard/stats");
    dashboardData = await res.json();
    updateDashboardKPIs(dashboardData.kpis);
    renderTopAtRiskTable(dashboardData.top_10_at_risk);
    renderDashboardCharts();
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
}

function updateDashboardKPIs(kpis) {
  document.getElementById("kpi-total-machines").textContent = kpis.total_machines;
  document.getElementById("kpi-healthy-machines").textContent = kpis.healthy_machines;
  document.getElementById("kpi-at-risk-machines").textContent = kpis.at_risk_machines;
  document.getElementById("kpi-critical-machines").textContent = kpis.critical_machines;
  document.getElementById("kpi-avg-health").textContent = kpis.avg_machine_health;
  document.getElementById("kpi-predicted-failures").textContent = kpis.predicted_failures_7d;
  document.getElementById("kpi-preventive-due").textContent = kpis.preventive_actions_due;
  document.getElementById("kpi-downtime").textContent = `${kpis.total_downtime_hours} h`;
  document.getElementById("kpi-maint-cost").textContent = `₹${(kpis.total_maintenance_cost_inr / 100000).toFixed(1)} L`;
}

function renderTopAtRiskTable(topMachines) {
  const tbody = document.getElementById("topAtRiskTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  topMachines.forEach(m => {
    const riskBadgeClass = m.risk_level === "Critical" ? "badge-critical" : (m.risk_level === "High" ? "badge-high" : "badge-mod");
    const priorityColor = m.priority_code === "P1" ? "text-red-400 bg-red-950/40" : (m.priority_code === "P2" ? "text-orange-400 bg-orange-950/40" : "text-yellow-400 bg-yellow-950/40");

    const tr = document.createElement("tr");
    tr.className = "hover:bg-[#1e293b]/50 transition-colors cursor-pointer";
    tr.onclick = (e) => {
      if (e.target.tagName !== "BUTTON") viewMachineProfile(m.machine_id);
    };

    tr.innerHTML = `
      <td class="py-2.5 px-3">
        <span class="font-bold text-white">${m.machine_id}</span>
        <div class="text-[10px] text-gray-400 font-sans">${m.machine_name}</div>
      </td>
      <td class="py-2.5 px-3 text-gray-300 font-sans">${m.machine_type}</td>
      <td class="py-2.5 px-3">
        <span class="font-bold ${m.health_score < 50 ? 'text-red-400' : 'text-amber-400'}">${m.health_score}/100</span>
      </td>
      <td class="py-2.5 px-3 font-bold text-rose-400">${m.failure_probability}%</td>
      <td class="py-2.5 px-3 text-amber-300 font-sans font-medium">${m.predicted_failure}</td>
      <td class="py-2.5 px-3">
        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${riskBadgeClass}">${m.risk_level.toUpperCase()}</span>
      </td>
      <td class="py-2.5 px-3">
        <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${priorityColor}">${m.priority_code}</span>
      </td>
      <td class="py-2.5 px-3">
        <button onclick="viewMachineProfile('${m.machine_id}')" class="px-2 py-1 bg-cyan-900/50 hover:bg-cyan-800 text-cyan-300 rounded text-[10px] font-sans font-semibold border border-cyan-700">
          Diagnose
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderDashboardCharts() {
  if (!dashboardData) return;

  // Chart A: Health Distribution Donut
  const ctxHealth = document.getElementById("chartHealthDistribution");
  if (ctxHealth) {
    if (charts.healthDist) charts.healthDist.destroy();
    const hDist = dashboardData.charts.health_distribution;
    charts.healthDist = new Chart(ctxHealth, {
      type: "doughnut",
      data: {
        labels: ["Excellent (90+)", "Good (75-89)", "Warning (60-74)", "Poor (40-59)", "Critical (<40)"],
        datasets: [{
          data: [hDist.Excellent, hDist.Good, hDist.Warning, hDist.Poor, hDist.Critical],
          backgroundColor: ["#10b981", "#3b82f6", "#eab308", "#f97316", "#ef4444"],
          borderWidth: 2,
          borderColor: "#111827"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#94a3b8", boxWidth: 10, font: { size: 9 } } }
        },
        cutout: "68%"
      }
    });
  }

  // Chart B: Failure Risk Distribution Donut
  const ctxRisk = document.getElementById("chartRiskDistribution");
  if (ctxRisk) {
    if (charts.riskDist) charts.riskDist.destroy();
    const rDist = dashboardData.charts.risk_distribution;
    charts.riskDist = new Chart(ctxRisk, {
      type: "doughnut",
      data: {
        labels: ["Low (0-25%)", "Moderate (26-50%)", "High (51-75%)", "Critical (76-100%)"],
        datasets: [{
          data: [rDist.Low, rDist.Moderate, rDist.High, rDist.Critical],
          backgroundColor: ["#10b981", "#eab308", "#f97316", "#ef4444"],
          borderWidth: 2,
          borderColor: "#111827"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#94a3b8", boxWidth: 10, font: { size: 9 } } }
        },
        cutout: "68%"
      }
    });
  }

  // Chart C & D: Health and Failure Risk Trend (6 Months Line)
  const ctxTrend = document.getElementById("chartHealthTrend");
  if (ctxTrend) {
    if (charts.healthTrend) charts.healthTrend.destroy();
    const tData = dashboardData.charts.health_trend;
    charts.healthTrend = new Chart(ctxTrend, {
      type: "line",
      data: {
        labels: tData.map(d => d.month),
        datasets: [
          {
            label: "Average Health Score (/100)",
            data: tData.map(d => d.avg_health),
            borderColor: "#06b6d4",
            backgroundColor: "rgba(6, 182, 212, 0.1)",
            fill: true,
            tension: 0.3,
            yAxisID: "y"
          },
          {
            label: "Failure Risk Probability (%)",
            data: tData.map(d => d.failure_risk_avg),
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.05)",
            borderDash: [4, 4],
            tension: 0.3,
            yAxisID: "y1"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 10 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#06b6d4", font: { size: 10 } }, min: 50, max: 100 },
          y1: { position: "right", grid: { drawOnChartArea: false }, ticks: { color: "#ef4444", font: { size: 10 } }, min: 0, max: 50 }
        },
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { size: 10 } } }
        }
      }
    });
  }

  // Chart 5: Thermal & Vibration Trajectory (CNC-004 vs Fleet)
  const ctxSensors = document.getElementById("chartSensorThermalVib");
  if (ctxSensors) {
    if (charts.sensorTrend) charts.sensorTrend.destroy();
    const sData = dashboardData.charts.sensor_trends;
    charts.sensorTrend = new Chart(ctxSensors, {
      type: "line",
      data: {
        labels: sData.map(d => d.date),
        datasets: [
          {
            label: "CNC-004 Temp (°C)",
            data: sData.map(d => d.temp_cnc004),
            borderColor: "#ef4444",
            borderWidth: 2,
            tension: 0.2
          },
          {
            label: "Fleet Avg Temp (°C)",
            data: sData.map(d => d.temp_fleet_avg),
            borderColor: "#3b82f6",
            borderDash: [3, 3],
            borderWidth: 1.5,
            tension: 0.2
          },
          {
            label: "CNC-004 Vib (mm/s x10)",
            data: sData.map(d => d.vib_cnc004 * 10),
            borderColor: "#a855f7",
            borderWidth: 2,
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } }
        },
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { size: 9 }, boxWidth: 10 } }
        }
      }
    });
  }

  // Chart 11: Production Load vs Failure Risk Correlation
  const ctxLoadRisk = document.getElementById("chartLoadVsRisk");
  if (ctxLoadRisk) {
    if (charts.loadRisk) charts.loadRisk.destroy();
    const lData = dashboardData.charts.load_vs_risk;
    charts.loadRisk = new Chart(ctxLoadRisk, {
      type: "bar",
      data: {
        labels: lData.map(d => d.load_bracket),
        datasets: [{
          label: "Average Failure Risk (%)",
          data: lData.map(d => d.avg_failure_risk),
          backgroundColor: ["#10b981", "#3b82f6", "#eab308", "#f97316", "#ef4444"],
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } }, max: 100 }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // Chart 9 & 10: Maintenance Monthly Spend & Downtime
  const ctxMaint = document.getElementById("chartMaintCostDowntime");
  if (ctxMaint) {
    if (charts.maintSpend) charts.maintSpend.destroy();
    const mData = dashboardData.charts.maintenance_monthly;
    charts.maintSpend = new Chart(ctxMaint, {
      type: "bar",
      data: {
        labels: mData.map(d => d.month),
        datasets: [
          {
            label: "Breakdown Spend (₹k)",
            data: mData.map(d => d.breakdown_cost / 1000),
            backgroundColor: "#ef4444",
            borderRadius: 3
          },
          {
            label: "Preventive Spend (₹k)",
            data: mData.map(d => d.preventive_cost / 1000),
            backgroundColor: "#06b6d4",
            borderRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } }
        },
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { size: 9 }, boxWidth: 10 } }
        }
      }
    });
  }
}

async function refreshDashboard() {
  await loadDashboardData();
  alert("Dashboard data synchronized with plant telemetry.");
}

// ==========================================
// 2. MACHINES FLEET DIRECTORY
// ==========================================
async function loadMachinesList() {
  try {
    const res = await fetch("/api/machines");
    const data = await res.json();
    allMachinesData = data.machines;
    renderMachinesTable(allMachinesData);
    populateMachineSelectors(allMachinesData);
  } catch (err) {
    console.error("Failed to load machines:", err);
  }
}

function renderMachinesTable(machines) {
  const tbody = document.getElementById("machinesTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  document.getElementById("machinesCountBadge").textContent = `${machines.length} Machines`;

  machines.forEach(m => {
    const riskBadgeClass = m.Risk_Level === "Critical" ? "badge-critical" : (m.Risk_Level === "High" ? "badge-high" : (m.Risk_Level === "Moderate" ? "badge-mod" : "badge-low"));
    const healthColor = m.Health_Score >= 75 ? "text-emerald-400" : (m.Health_Score >= 60 ? "text-amber-400" : "text-red-400");

    const tr = document.createElement("tr");
    tr.className = "hover:bg-[#1e293b]/60 transition-colors";
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-mono font-bold text-cyan-400 cursor-pointer" onclick="viewMachineProfile('${m.Machine_ID}')">${m.Machine_ID}</td>
      <td class="py-2.5 px-3 font-medium text-white">${m.Machine_Name}</td>
      <td class="py-2.5 px-3 text-gray-300">
        <div>${m.Machine_Type}</div>
        <div class="text-[10px] text-gray-500">${m.Production_Line}</div>
      </td>
      <td class="py-2.5 px-3 text-gray-300">
        <div>${m.Manufacturer}</div>
        <div class="text-[10px] text-gray-500">${m.Model}</div>
      </td>
      <td class="py-2.5 px-3 text-gray-300">
        <div>${m.Machine_Age}</div>
        <div class="text-[10px] ${m.Warranty_Status === 'Active' ? 'text-emerald-400' : 'text-gray-500'} font-semibold">${m.Warranty_Status}</div>
      </td>
      <td class="py-2.5 px-3 text-gray-300 font-mono">${m.Operating_Hours.toLocaleString()} hrs</td>
      <td class="py-2.5 px-3 font-bold font-mono ${healthColor}">${m.Health_Score}</td>
      <td class="py-2.5 px-3 font-bold font-mono text-rose-400">${m.Failure_Probability}%</td>
      <td class="py-2.5 px-3">
        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${riskBadgeClass}">${m.Risk_Level.toUpperCase()}</span>
      </td>
      <td class="py-2.5 px-3 text-right space-x-1">
        <button onclick="viewMachineProfile('${m.Machine_ID}')" class="px-2 py-1 bg-cyan-900/60 hover:bg-cyan-800 text-cyan-300 rounded text-[10px] font-medium border border-cyan-700">
          Profile
        </button>
        <button onclick="openReportCardModal('${m.Machine_ID}')" class="px-2 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-[10px] font-medium border border-gray-700">
          Card
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function filterMachines() {
  const typeVal = document.getElementById("filterMachineType").value;
  const riskVal = document.getElementById("filterRiskLevel").value;
  const healthVal = document.getElementById("filterHealthStatus").value;
  const lineVal = document.getElementById("filterProductionLine").value;
  const critVal = document.getElementById("filterCriticality").value;
  const searchVal = document.getElementById("globalSearchInput") ? document.getElementById("globalSearchInput").value.toLowerCase().trim() : "";

  let filtered = allMachinesData.filter(m => {
    if (typeVal !== "All" && m.Machine_Type !== typeVal) return false;
    if (riskVal !== "All" && m.Risk_Level !== riskVal) return false;
    if (healthVal !== "All" && m.Health_Category !== healthVal) return false;
    if (lineVal !== "All" && m.Production_Line !== lineVal) return false;
    if (critVal !== "All" && m.Criticality_Level !== critVal) return false;
    if (searchVal) {
      const match = m.Machine_ID.toLowerCase().includes(searchVal) ||
                    m.Machine_Name.toLowerCase().includes(searchVal) ||
                    m.Model.toLowerCase().includes(searchVal) ||
                    m.Manufacturer.toLowerCase().includes(searchVal);
      if (!match) return false;
    }
    return true;
  });

  renderMachinesTable(filtered);
}

function resetMachineFilters() {
  document.getElementById("filterMachineType").value = "All";
  document.getElementById("filterRiskLevel").value = "All";
  document.getElementById("filterHealthStatus").value = "All";
  document.getElementById("filterProductionLine").value = "All";
  document.getElementById("filterCriticality").value = "All";
  if (document.getElementById("globalSearchInput")) document.getElementById("globalSearchInput").value = "";
  renderMachinesTable(allMachinesData);
}

function populateMachineSelectors(machines) {
  const selects = ["whatIfMachineSelect", "sensorMachineSelector"];
  selects.forEach(sId => {
    const el = document.getElementById(sId);
    if (!el) return;
    el.innerHTML = "";
    machines.forEach(m => {
      const opt = document.createElement("option");
      opt.value = m.Machine_ID;
      opt.textContent = `${m.Machine_ID} - ${m.Machine_Name} (${m.Risk_Level})`;
      if (m.Machine_ID === currentMachineId) opt.selected = true;
      el.appendChild(opt);
    });
  });
}

// ==========================================
// 3. MACHINE PROFILE & EXPLAINABLE AI (XAI)
// ==========================================
async function viewMachineProfile(mId) {
  currentMachineId = mId;
  navigateTo("machine-details");

  try {
    const res = await fetch(`/api/machines/${mId}`);
    const data = await res.json();
    const m = data.machine_master;
    const pred = data.prediction;
    const rec = data.recommendations;
    const devs = data.sensor_deviations;

    // Header info
    document.getElementById("profileMachineId").textContent = m.Machine_ID;
    document.getElementById("profileMachineName").textContent = `${m.Machine_Name} — ${m.Department} (${m.Production_Line})`;
    
    const riskBadge = document.getElementById("profileRiskBadge");
    riskBadge.textContent = `${pred.risk_level.toUpperCase()} RISK`;
    riskBadge.className = `text-xs px-2.5 py-0.5 rounded font-bold ${pred.risk_level === 'Critical' ? 'badge-critical' : (pred.risk_level === 'High' ? 'badge-high' : 'badge-mod')}`;

    // Health Score
    document.getElementById("profileHealthScore").textContent = m.Current_Machine_Health_Score;
    document.getElementById("profileHealthCategory").textContent = data.health_category.toUpperCase();
    document.getElementById("profileHealthBar").style.width = `${m.Current_Machine_Health_Score}%`;

    // Failure Probability
    document.getElementById("profileFailureProb").textContent = `${pred.failure_probability}%`;
    document.getElementById("profileConfidence").textContent = `${pred.confidence_score}%`;
    document.getElementById("profileProbBar").style.width = `${pred.failure_probability}%`;

    // Diagnosed Failure
    document.getElementById("profilePredictedFailure").textContent = pred.predicted_failure;
    document.getElementById("profilePriorityCode").textContent = `${rec.priority_code} (${rec.urgency})`;

    // Live Sensors Grid
    renderProfileSensorsGrid(devs);

    // Explainable AI Decomposition
    renderProfileXaiFactors(m, pred);

    // Directives
    document.getElementById("profileUrgencyBadge").textContent = rec.urgency;
    document.getElementById("profileRecAction").textContent = rec.recommended_action;
    document.getElementById("profileRecWhy").textContent = rec.root_cause_explanation;
    document.getElementById("profileRecConsequence").textContent = rec.risk_if_ignored;
    document.getElementById("profileEstDowntime").textContent = `${rec.estimated_downtime_hours} hrs`;
    document.getElementById("profileUnitsRisk").textContent = `${rec.units_at_risk.toLocaleString()} pcs`;
    document.getElementById("profileBreakdownCost").textContent = `₹${rec.estimated_breakdown_cost_inr.toLocaleString()}`;

    // Load Telemetry Chart
    await loadMachineTelemetryChart("30d");

  } catch (err) {
    console.error("Failed to load machine profile:", err);
  }
}

function renderProfileSensorsGrid(devs) {
  const container = document.getElementById("profileSensorsGrid");
  if (!container) return;
  container.innerHTML = "";

  Object.entries(devs).forEach(([sKey, sInfo]) => {
    const isAbnormal = sInfo.status !== "Normal";
    const borderClass = sInfo.status === "Critical Anomaly" ? "border-red-600 bg-red-950/20" : (sInfo.status === "Warning" ? "border-amber-600 bg-amber-950/20" : "border-gray-800 bg-[#1e293b]/40");
    const label = sKey.replace('_', ' ').toUpperCase();
    const devSign = sInfo.deviation_pct > 0 ? "+" : "";

    const card = document.createElement("div");
    card.className = `p-3 rounded-lg border ${borderClass} flex flex-col justify-between`;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-[10px] text-gray-400 font-semibold tracking-wider">${label}</span>
        <span class="text-[9px] px-1.5 py-0.2 rounded font-bold ${sInfo.status === 'Critical Anomaly' ? 'bg-red-900 text-red-200' : (sInfo.status === 'Warning' ? 'bg-amber-900 text-amber-200' : 'bg-emerald-950 text-emerald-300')}">
          ${sInfo.status.toUpperCase()}
        </span>
      </div>
      <div class="my-2">
        <div class="text-xl font-bold font-mono text-white">${sInfo.value} <span class="text-xs text-gray-400 font-normal">${sInfo.unit}</span></div>
        <div class="text-[10px] text-gray-500 font-mono">Nominal: ${sInfo.normal_range}</div>
      </div>
      <div class="text-[10px] font-semibold ${isAbnormal ? 'text-rose-400' : 'text-emerald-400'}">
        Deviation: ${devSign}${sInfo.deviation_pct}%
      </div>
    `;
    container.appendChild(card);
  });
}

function renderProfileXaiFactors(machine, pred) {
  const listContainer = document.getElementById("profileXaiFactorsList");
  if (!listContainer) return;
  listContainer.innerHTML = "";

  document.getElementById("profileXaiExplanation").textContent = 
    `${machine.Machine_ID} has a ${pred.failure_probability}% predicted failure probability decomposed into the following additive risk drivers:`;

  pred.contributing_factors.forEach(f => {
    const div = document.createElement("div");
    div.className = "p-2 rounded bg-[#1e293b] border border-gray-700/60 flex items-center justify-between";
    div.innerHTML = `
      <div class="flex items-center space-x-2">
        <span class="text-xs font-semibold text-rose-400 font-mono">+${f.risk_contribution}%</span>
        <span class="text-gray-300 font-medium">${f.factor}</span>
      </div>
      <span class="text-[10px] text-gray-400 px-1.5 py-0.5 rounded bg-gray-800">${f.category}</span>
    `;
    listContainer.appendChild(div);
  });
}

async function loadMachineTelemetryChart(rangePeriod) {
  try {
    const res = await fetch(`/api/machines/${currentMachineId}/telemetry?range_period=${rangePeriod}`);
    const data = await res.json();
    const pts = data.telemetry_points;
    const ctx = document.getElementById("chartProfileTelemetry");
    if (!ctx) return;

    if (charts.profileTelemetry) charts.profileTelemetry.destroy();

    const labels = pts.map(p => p.timestamp.slice(5)); // MM-DD HH:MM
    const tempVals = pts.map(p => p.readings.temp);
    const vibVals = pts.map(p => p.readings.vibration);

    charts.profileTelemetry = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Actual Temperature (°C)",
            data: tempVals,
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            borderWidth: 2.5,
            tension: 0.2,
            yAxisID: "y"
          },
          {
            label: "Actual Vibration (mm/s)",
            data: vibVals,
            borderColor: "#a855f7",
            borderWidth: 2,
            tension: 0.2,
            yAxisID: "y1"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#ef4444", font: { size: 9 } }, title: { display: true, text: "Temp °C", color: "#ef4444", font: { size: 9 } } },
          y1: { position: "right", grid: { drawOnChartArea: false }, ticks: { color: "#a855f7", font: { size: 9 } }, title: { display: true, text: "Vib mm/s", color: "#a855f7", font: { size: 9 } } }
        },
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { size: 10 } } }
        }
      }
    });
  } catch (err) {
    console.error("Failed to load profile telemetry:", err);
  }
}

// ==========================================
// 4. MULTI-SENSOR ANALYTICS CHARTS (Section 12)
// ==========================================
async function switchSensorAnalyticsMachine(mId) {
  try {
    const res = await fetch(`/api/machines/${mId}/telemetry?range_period=90d`);
    const data = await res.json();
    renderSensorAnalyticsCharts(data);
  } catch (err) {
    console.error("Failed to load sensor analytics:", err);
  }
}

function renderSensorAnalyticsCharts(data) {
  if (!data || !data.telemetry_points) return;
  const pts = data.telemetry_points;
  const labels = pts.map(p => p.timestamp.slice(5));

  // 1. Temperature Chart
  const ctxT = document.getElementById("chartSensorTemp");
  if (ctxT) {
    if (charts.sTemp) charts.sTemp.destroy();
    charts.sTemp = new Chart(ctxT, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Temperature (°C)",
          data: pts.map(p => p.readings.temp),
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // 2. Vibration Chart
  const ctxV = document.getElementById("chartSensorVib");
  if (ctxV) {
    if (charts.sVib) charts.sVib.destroy();
    charts.sVib = new Chart(ctxV, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Vibration (mm/s)",
          data: pts.map(p => p.readings.vibration),
          borderColor: "#a855f7",
          backgroundColor: "rgba(168, 85, 247, 0.15)",
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // 3. RPM Chart
  const ctxR = document.getElementById("chartSensorRPM");
  if (ctxR) {
    if (charts.sRpm) charts.sRpm.destroy();
    charts.sRpm = new Chart(ctxR, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "RPM",
          data: pts.map(p => p.readings.rpm),
          borderColor: "#06b6d4",
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // 4. Power & Current Chart
  const ctxP = document.getElementById("chartSensorPower");
  if (ctxP) {
    if (charts.sPow) charts.sPow.destroy();
    charts.sPow = new Chart(ctxP, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Power (kW)",
            data: pts.map(p => p.readings.power),
            borderColor: "#f59e0b",
            tension: 0.3
          },
          {
            label: "Current (A)",
            data: pts.map(p => p.readings.current),
            borderColor: "#3b82f6",
            borderDash: [3, 3],
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } },
          y: { grid: { color: "#1f2937" }, ticks: { color: "#94a3b8", font: { size: 9 } } }
        },
        plugins: { legend: { labels: { color: "#94a3b8", font: { size: 9 }, boxWidth: 10 } } }
      }
    });
  }
}

// ==========================================
// 5. MAINTENANCE PRIORITIZATION QUEUE
// ==========================================
async function loadPrioritizationQueue() {
  if (!dashboardData) await loadDashboardData();
  const queue = dashboardData.top_10_at_risk;
  const tbody = document.getElementById("priorityQueueTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  queue.forEach(item => {
    const pBg = item.priority_code === "P1" ? "bg-red-950 text-red-400 border border-red-800" : (item.priority_code === "P2" ? "bg-orange-950 text-orange-400 border border-orange-800" : "bg-yellow-950 text-yellow-400 border border-yellow-800");

    const tr = document.createElement("tr");
    tr.className = "hover:bg-[#1e293b]/60 transition-colors";
    tr.innerHTML = `
      <td class="py-2.5 px-3">
        <span class="px-2 py-0.5 rounded font-bold text-[10px] ${pBg}">${item.priority_code}</span>
      </td>
      <td class="py-2.5 px-3">
        <span class="font-bold text-white">${item.machine_id}</span>
        <div class="text-[10px] text-gray-400 font-sans">${item.production_line}</div>
      </td>
      <td class="py-2.5 px-3 font-bold text-cyan-400">${item.priority_score}</td>
      <td class="py-2.5 px-3 font-bold text-rose-400">${item.failure_probability}%</td>
      <td class="py-2.5 px-3 text-amber-300 font-sans font-medium">${item.predicted_failure}</td>
      <td class="py-2.5 px-3 text-gray-300">${item.recommended_date}</td>
      <td class="py-2.5 px-3 text-gray-300 font-sans max-w-xs truncate">${item.recommended_action}</td>
      <td class="py-2.5 px-3 text-orange-400">${item.downtime_hours}h (₹${item.breakdown_cost.toLocaleString()})</td>
      <td class="py-2.5 px-3 text-right">
        <button onclick="viewMachineProfile('${item.machine_id}')" class="px-2 py-1 bg-cyan-900/50 hover:bg-cyan-800 text-cyan-300 rounded text-[10px] font-sans font-medium">
          Open Work Order
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// ==========================================
// 6. MAINTENANCE PLANNER
// ==========================================
async function loadMaintenancePlanner(filterPeriod = "all") {
  try {
    const res = await fetch("/api/maintenance/schedule");
    const data = await res.json();

    document.getElementById("plannerOverdueCount").textContent = data.counts.overdue;
    document.getElementById("plannerTodayCount").textContent = data.counts.today;
    document.getElementById("plannerNext7Count").textContent = data.counts.next_7_days;

    renderPlannerCards("plannerOverdueContainer", data.overdue, "overdue");
    renderPlannerCards("plannerTodayContainer", data.today, "today");
    renderPlannerCards("plannerNext7Container", data.next_7_days, "upcoming");

    // Also populate priority queue on predictive-maint page
    loadPrioritizationQueue();
  } catch (err) {
    console.error("Failed to load maintenance planner:", err);
  }
}

function renderPlannerCards(containerId, items, category) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = "";

  if (items.length === 0) {
    container.innerHTML = `<div class="p-3 text-xs text-gray-500 text-center">No maintenance tasks scheduled.</div>`;
    return;
  }

  items.forEach(item => {
    const borderClass = category === "overdue" ? "border-red-900/50 bg-red-950/10" : (category === "today" ? "border-cyan-900/50 bg-cyan-950/10" : "border-gray-800 bg-[#1e293b]/40");
    const badgeColor = category === "overdue" ? "text-red-400 bg-red-950" : (category === "today" ? "text-cyan-400 bg-cyan-950" : "text-indigo-400 bg-indigo-950");

    const card = document.createElement("div");
    card.className = `p-3 rounded-lg border ${borderClass} space-y-1 text-xs`;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-white">${item.machine_id}</span>
        <span class="text-[10px] px-1.5 py-0.2 rounded font-bold font-mono ${badgeColor}">${item.priority_code}</span>
      </div>
      <div class="text-[11px] text-gray-400 font-medium">${item.machine_type} (${item.department})</div>
      <div class="text-[11px] text-amber-300 font-medium">${item.predicted_failure}</div>
      <div class="text-[10px] text-gray-400 pt-1 flex justify-between">
        <span>Due: <b class="text-white">${item.scheduled_date}</b></span>
        <span>Duration: <b class="text-white">${item.estimated_duration_hours}h</b></span>
      </div>
      <div class="pt-2 flex justify-end space-x-1">
        <button onclick="viewMachineProfile('${item.machine_id}')" class="px-2 py-0.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-[10px]">Details</button>
        <button onclick="alert('Maintenance Work Order dispatched for ${item.machine_id}')" class="px-2 py-0.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[10px]">Dispatch</button>
      </div>
    `;
    container.appendChild(card);
  });
}

// ==========================================
// 7. ALERT SURVEILLANCE CENTER
// ==========================================
async function loadAlerts() {
  try {
    const res = await fetch("/api/alerts");
    const data = await res.json();
    const alerts = data.alerts;

    document.getElementById("sidebarAlertCount").textContent = alerts.filter(a => a.status === "Active").length;
    document.getElementById("headerAlertBadge").textContent = alerts.filter(a => a.status === "Active").length;
    document.getElementById("activeAlertBadge").textContent = `${alerts.filter(a => a.status === "Active").length} Active Alarms`;

    const container = document.getElementById("alertsListContainer");
    if (!container) return;
    container.innerHTML = "";

    alerts.forEach(a => {
      const isAck = a.status === "Acknowledged";
      const borderClass = a.severity === "CRITICAL" ? "border-red-600/70 bg-red-950/20" : "border-orange-600/60 bg-orange-950/20";

      const card = document.createElement("div");
      card.className = `p-4 rounded-xl border ${borderClass} space-y-2 text-xs transition-all`;
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="text-lg">${a.badge}</span>
            <span class="font-bold text-white text-sm">${a.title}</span>
            <span class="text-[10px] px-2 py-0.5 rounded font-mono font-bold ${a.severity === 'CRITICAL' ? 'bg-red-900 text-red-200' : 'bg-orange-900 text-orange-200'}">
              ${a.severity}
            </span>
          </div>
          <span class="text-[11px] text-gray-400 font-mono">${a.timestamp}</span>
        </div>
        <p class="text-gray-300 leading-relaxed">${a.message}</p>
        <div class="p-2.5 rounded bg-[#111827] border border-gray-800 text-[11px] text-gray-300 flex items-center justify-between">
          <span><b class="text-cyan-400">Prescribed Intervention:</b> ${a.recommended_action}</span>
          <div class="space-x-1 shrink-0 ml-2">
            ${isAck ? 
              `<span class="text-emerald-400 text-[10px] font-bold"><i class="fa-solid fa-check mr-1"></i>Acknowledged</span>` :
              `<button onclick="acknowledgeAlert('${a.alert_id}')" class="px-2.5 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-[10px] border border-gray-700 font-semibold">Acknowledge</button>`
            }
            <button onclick="viewMachineProfile('${a.machine_id}')" class="px-2.5 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[10px] font-semibold">Investigate</button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load alerts:", err);
  }
}

async function acknowledgeAlert(alertId) {
  try {
    const res = await fetch(`/api/alerts/acknowledge/${alertId}`, { method: "POST" });
    if (res.ok) {
      await loadAlerts();
    }
  } catch (err) {
    console.error("Failed to acknowledge alert:", err);
  }
}

async function refreshAlerts() {
  await loadAlerts();
}

// ==========================================
// 8. PRODUCTION IMPACT ANALYSIS
// ==========================================
async function loadProductionImpact() {
  try {
    const res = await fetch("/api/production-impact");
    const data = await res.json();

    document.getElementById("prodTotalUnits").textContent = `${data.total_units_at_risk.toLocaleString()} Units`;
    document.getElementById("prodTotalDowntime").textContent = `${data.total_downtime_hours} Hours`;
    document.getElementById("prodTotalLoss").textContent = `₹${data.total_potential_loss_inr.toLocaleString()}`;

    const tbody = document.getElementById("productionLinesTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.lines_summary.forEach(l => {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-[#1e293b]/60 transition-colors";
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-sans font-bold text-white">${l.line_name}</td>
        <td class="py-2.5 px-3 text-gray-300">${l.total_machines} Assets</td>
        <td class="py-2.5 px-3 text-amber-400 font-bold">${l.at_risk_machines} Machines</td>
        <td class="py-2.5 px-3 text-red-400 font-bold">${l.critical_machines} Machines</td>
        <td class="py-2.5 px-3 font-bold text-cyan-400">${l.utilization_avg}/100</td>
        <td class="py-2.5 px-3 text-orange-400">${l.potential_downtime_hours} hrs</td>
        <td class="py-2.5 px-3 text-amber-300">${l.total_units_at_risk.toLocaleString()} pcs</td>
        <td class="py-2.5 px-3 text-red-400 font-bold">₹${l.potential_financial_loss_inr.toLocaleString()}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load production impact:", err);
  }
}

// ==========================================
// 9. WHAT-IF SCENARIO SIMULATOR (Section 20)
// ==========================================
async function loadWhatIfMachine(mId) {
  try {
    const res = await fetch(`/api/machines/${mId}`);
    const data = await res.json();
    const m = data.machine_master;
    const devs = data.sensor_deviations;

    document.getElementById("whatifBaseHealth").textContent = m.Current_Machine_Health_Score;
    document.getElementById("whatifBaseProb").textContent = `${m.Current_Failure_Probability}%`;
    document.getElementById("whatifBaseRisk").textContent = m.Current_Risk_Level;

    // Set slider defaults from actual sensors
    const tempVal = devs.temp ? devs.temp.value : 70;
    const vibVal = devs.vibration ? devs.vibration.value : 2.5;
    const rpmVal = devs.rpm ? devs.rpm.value : 3000;
    const loadVal = devs.load ? devs.load.value : 80;
    const oilVal = devs.oil_level ? devs.oil_level.value : 80;

    document.getElementById("sliderTemp").value = tempVal;
    document.getElementById("sliderTempVal").textContent = `${tempVal} °C`;

    document.getElementById("sliderVib").value = vibVal;
    document.getElementById("sliderVibVal").textContent = `${vibVal} mm/s`;

    document.getElementById("sliderRpm").value = rpmVal;
    document.getElementById("sliderRpmVal").textContent = `${rpmVal} RPM`;

    document.getElementById("sliderLoad").value = loadVal;
    document.getElementById("sliderLoadVal").textContent = `${loadVal} %`;

    document.getElementById("sliderOil").value = oilVal;
    document.getElementById("sliderOilVal").textContent = `${oilVal} %`;

    runWhatIfSimulation();
  } catch (err) {
    console.error("Failed to load what-if machine:", err);
  }
}

async function runWhatIfSimulation() {
  const mId = document.getElementById("whatIfMachineSelect").value || currentMachineId;
  const temp = parseFloat(document.getElementById("sliderTemp").value);
  const vib = parseFloat(document.getElementById("sliderVib").value);
  const rpm = parseFloat(document.getElementById("sliderRpm").value);
  const load = parseFloat(document.getElementById("sliderLoad").value);
  const oil = parseFloat(document.getElementById("sliderOil").value);
  const days = parseInt(document.getElementById("sliderDays").value);

  // Update slider labels
  document.getElementById("sliderTempVal").textContent = `${temp} °C`;
  document.getElementById("sliderVibVal").textContent = `${vib} mm/s`;
  document.getElementById("sliderRpmVal").textContent = `${rpm} RPM`;
  document.getElementById("sliderLoadVal").textContent = `${load} %`;
  document.getElementById("sliderOilVal").textContent = `${oil} %`;
  document.getElementById("sliderDaysVal").textContent = `${days} Days`;

  try {
    const res = await fetch("/api/what-if", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        machine_id: mId,
        temperature: temp,
        vibration: vib,
        rpm: rpm,
        production_load: load,
        oil_level: oil,
        days_since_maint: days
      })
    });
    const result = await res.json();
    const sim = result.simulation_result;

    document.getElementById("whatifSimHealth").textContent = sim.health_score;
    document.getElementById("whatifSimProb").textContent = `${sim.failure_probability}%`;
    document.getElementById("whatifSimRisk").textContent = sim.risk_level;
    document.getElementById("whatifSimType").textContent = sim.predicted_failure;
    document.getElementById("whatifSimRec").textContent = sim.recommendation.recommended_action;

    // Delta indicators
    const dH = sim.delta_health;
    const dP = sim.delta_probability;
    const elDH = document.getElementById("whatifDeltaHealth");
    const elDP = document.getElementById("whatifDeltaProb");

    elDH.textContent = `${dH > 0 ? '+' : ''}${dH}`;
    elDH.className = `font-mono font-bold ${dH > 0 ? 'text-emerald-400' : (dH < 0 ? 'text-red-400' : 'text-gray-300')}`;

    elDP.textContent = `${dP > 0 ? '+' : ''}${dP}%`;
    elDP.className = `font-mono font-bold ${dP > 0 ? 'text-red-400' : (dP < 0 ? 'text-emerald-400' : 'text-gray-300')}`;
  } catch (err) {
    console.error("Failed to run what-if simulation:", err);
  }
}

function resetWhatIfSliders() {
  loadWhatIfMachine(document.getElementById("whatIfMachineSelect").value || currentMachineId);
}

function openWhatIfModalForCurrent() {
  const sel = document.getElementById("whatIfMachineSelect");
  if (sel) sel.value = currentMachineId;
  loadWhatIfMachine(currentMachineId);
  navigateTo("what-if");
}

// ==========================================
// 10. REPORT CARDS & BULK GENERATION (Section 13 & 14)
// ==========================================
function renderReportCardsGrid() {
  const container = document.getElementById("reportCardsGrid");
  if (!container) return;
  container.innerHTML = "";

  allMachinesData.forEach(m => {
    const isCritical = m.Risk_Level === "Critical";
    const borderClass = isCritical ? "border-red-900/60 bg-red-950/20" : (m.Risk_Level === "High" ? "border-orange-900/60 bg-orange-950/20" : "border-gray-800 bg-[#1e293b]/40");

    const card = document.createElement("div");
    card.className = `p-3 rounded-lg border ${borderClass} flex flex-col justify-between text-xs space-y-2`;
    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between">
          <span class="font-bold text-white font-mono">${m.Machine_ID}</span>
          <span class="text-[9px] px-1.5 py-0.2 rounded font-bold ${isCritical ? 'bg-red-900 text-red-200' : 'bg-gray-800 text-gray-300'}">${m.Risk_Level}</span>
        </div>
        <div class="text-[11px] text-gray-300 font-medium mt-1 truncate">${m.Machine_Name}</div>
        <div class="text-[10px] text-gray-500">${m.Machine_Type}</div>
      </div>
      <div class="pt-2 border-t border-gray-800/80 flex items-center justify-between text-[11px]">
        <span>Health: <b class="text-white">${m.Health_Score}</b></span>
        <span>Risk: <b class="text-rose-400">${m.Failure_Probability}%</b></span>
      </div>
      <div class="pt-1 flex space-x-1">
        <button onclick="openReportCardModal('${m.Machine_ID}')" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[10px] py-1 font-medium">
          View Audit Card
        </button>
        <button onclick="downloadMachinePDF('${m.Machine_ID}')" class="px-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded text-[10px] py-1 border border-gray-700">
          <i class="fa-solid fa-file-pdf text-rose-400"></i>
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

function filterReportCardsList(query) {
  const q = query.toLowerCase();
  const cards = document.querySelectorAll("#reportCardsGrid > div");
  cards.forEach(card => {
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(q) ? "flex" : "none";
  });
}

async function openReportCardModal(mId) {
  currentModalMachineId = mId;
  try {
    const res = await fetch(`/api/machines/${mId}/report-card`);
    const cardData = await res.json();
    renderPrintableReportCard(cardData);
    document.getElementById("reportCardModal").classList.remove("hidden");
  } catch (err) {
    console.error("Failed to load report card data:", err);
  }
}

function closeReportCardModal() {
  document.getElementById("reportCardModal").classList.add("hidden");
}

function renderPrintableReportCard(d) {
  const container = document.getElementById("printableReportCard");
  if (!container) return;
  const m = d.machine;
  const s = d.sensor_status;
  const rec = d.ai_recommendations;
  const isCrit = d.risk_level === "Critical";

  container.innerHTML = `
    <!-- HEADER -->
    <div class="border-b-2 border-slate-900 pb-3 mb-4 flex justify-between items-start">
      <div>
        <h1 class="text-xl font-extrabold tracking-tight text-slate-900 uppercase">ABC AUTOMOTIVE COMPONENTS PVT. LTD.</h1>
        <p class="text-xs font-semibold text-slate-600">Reliability Engineering Division — AI Predictive Intelligence Center</p>
      </div>
      <div class="text-right text-[11px] text-slate-600">
        <div><b>AUDIT DATE:</b> ${d.generated_at}</div>
        <div><b>LOCATION:</b> Plant-01 Precision Line</div>
      </div>
    </div>

    <!-- TITLE BANNER -->
    <div class="bg-slate-900 text-white p-2.5 rounded mb-4 flex justify-between items-center">
      <span class="font-extrabold text-sm tracking-wider">MACHINE HEALTH REPORT CARD: ${m.Machine_ID}</span>
      <span class="px-2 py-0.5 rounded text-xs font-black uppercase ${isCrit ? 'bg-red-600 text-white' : 'bg-amber-500 text-black'}">
        ${d.risk_level} RISK
      </span>
    </div>

    <!-- 4 KPI SUMMARY BLOCKS -->
    <div class="grid grid-cols-4 gap-3 mb-4 text-center">
      <div class="border border-slate-300 p-2 rounded bg-slate-50">
        <div class="text-[10px] text-slate-500 font-bold uppercase">Health Score</div>
        <div class="text-2xl font-black text-slate-900">${d.health_score} / 100</div>
      </div>
      <div class="border border-slate-300 p-2 rounded bg-slate-50">
        <div class="text-[10px] text-slate-500 font-bold uppercase">Failure Probability (7d)</div>
        <div class="text-2xl font-black text-red-600">${d.failure_probability}%</div>
      </div>
      <div class="border border-slate-300 p-2 rounded bg-slate-50">
        <div class="text-[10px] text-slate-500 font-bold uppercase">Risk Level</div>
        <div class="text-lg font-black text-slate-800 uppercase">${d.risk_level}</div>
      </div>
      <div class="border border-slate-300 p-2 rounded bg-slate-50">
        <div class="text-[10px] text-slate-500 font-bold uppercase">Maintenance Priority</div>
        <div class="text-lg font-black text-blue-700">${rec.priority_code}</div>
      </div>
    </div>

    <!-- SECTION 1: ASSET SPECIFICATIONS -->
    <div class="mb-4">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800 border-b border-slate-300 pb-1 mb-2">1. Asset Master Profile</h3>
      <div class="grid grid-cols-3 gap-2 text-xs">
        <div><b>Machine Name:</b> ${m.Machine_Name}</div>
        <div><b>Type:</b> ${m.Machine_Type}</div>
        <div><b>Department:</b> ${m.Department}</div>
        <div><b>Manufacturer:</b> ${m.Manufacturer}</div>
        <div><b>Model:</b> ${m.Model}</div>
        <div><b>Production Line:</b> ${m.Production_Line}</div>
        <div><b>Asset Age:</b> ${m.Machine_Age}</div>
        <div><b>Warranty:</b> ${m.Warranty_Status}</div>
        <div><b>Operating Hours:</b> ${m.Operating_Hours.toLocaleString()} hrs</div>
      </div>
    </div>

    <!-- SECTION 2: SENSOR TELEMETRY TABLE -->
    <div class="mb-4">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800 border-b border-slate-300 pb-1 mb-2">2. Telemetry Deviation Audit</h3>
      <table class="w-full text-xs text-left border border-slate-300">
        <thead class="bg-slate-100 border-b border-slate-300">
          <tr>
            <th class="p-1.5">Sensor</th>
            <th class="p-1.5">Observed Value</th>
            <th class="p-1.5">Nominal Band</th>
            <th class="p-1.5">Baseline Deviation</th>
            <th class="p-1.5">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          ${Object.entries(s).map(([sKey, info]) => `
            <tr>
              <td class="p-1.5 font-semibold">${sKey.replace('_', ' ').toUpperCase()}</td>
              <td class="p-1.5 font-mono">${info.value} ${info.unit}</td>
              <td class="p-1.5 text-slate-500">${info.normal_range}</td>
              <td class="p-1.5 font-mono ${info.deviation_pct > 0 ? 'text-red-600' : 'text-slate-800'}">${info.deviation_pct > 0 ? '+' : ''}${info.deviation_pct}%</td>
              <td class="p-1.5 font-bold ${info.status !== 'Normal' ? 'text-red-600' : 'text-emerald-700'}">${info.status}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>

    <!-- SECTION 3: KEY WARNING SIGNS & DIAGNOSIS -->
    <div class="mb-4">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800 border-b border-slate-300 pb-1 mb-2">3. Primary Failure Mode & Warning Signs</h3>
      <div class="p-2.5 rounded bg-slate-100 border border-slate-300 text-xs mb-2">
        <span class="font-bold text-red-700">Predicted Failure:</span> <b>${d.predicted_failure}</b> (Diagnostic Confidence: ${d.confidence_score}%)
      </div>
      <ul class="text-xs space-y-1 list-disc pl-5 text-slate-800">
        ${d.key_warning_signs.map(w => `<li><b>${w.sensor}:</b> ${w.text}</li>`).join('')}
      </ul>
    </div>

    <!-- SECTION 4: AI RECOMMENDATION & RISK IF IGNORED -->
    <div class="mb-4 border border-slate-300 rounded p-3 bg-slate-50 text-xs space-y-2">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-800 border-b border-slate-200 pb-1">4. Prescriptive Action Directives</h3>
      <div><b>Urgency / Window:</b> <span class="text-red-700 font-bold">${rec.urgency} — ${rec.timeframe}</span></div>
      <div><b>Recommended Action:</b> ${rec.recommended_action}</div>
      <div><b>Technical Rationale:</b> ${rec.root_cause_explanation}</div>
      <div><b>Consequence If Ignored:</b> <span class="text-red-700 font-semibold">${rec.risk_if_ignored}</span></div>
      <div class="pt-2 border-t border-slate-200 flex justify-between font-mono text-[11px]">
        <span>Downtime Risk: <b>${d.potential_impact.estimated_downtime_hours} hrs</b></span>
        <span>Units at Risk: <b>${d.potential_impact.units_at_risk} pcs</b></span>
        <span>Estimated Breakdown Exposure: <b>₹${d.potential_impact.estimated_breakdown_cost_inr.toLocaleString()}</b></span>
      </div>
    </div>

    <!-- FOOTER SIGN-OFF -->
    <div class="pt-2 border-t border-slate-300 text-[9px] text-slate-500 flex justify-between items-center">
      <span>ABC Automotive Components Pvt. Ltd. | Confidential Technical Audit</span>
      <span>Verified by AI Predictive Maintenance Engine</span>
    </div>
  `;
}

function downloadCurrentModalPDF() {
  downloadMachinePDF(currentModalMachineId);
}

function downloadCurrentMachinePDF() {
  downloadMachinePDF(currentMachineId);
}

function downloadMachinePDF(mId) {
  window.open(`/api/machines/${mId}/pdf`, "_blank");
}

function downloadBulkReports(riskLevel = "All") {
  window.open(`/api/reports/bulk-pdf?risk_level=${riskLevel}`, "_blank");
}

function downloadManagementReport(reportType) {
  window.open(`/api/reports/management/${reportType}/pdf`, "_blank");
}

// ==========================================
// 11. DATA QUALITY CENTER (Section 24)
// ==========================================
async function loadDataQuality() {
  try {
    const res = await fetch("/api/data-quality");
    const data = await res.json();

    document.getElementById("dqScore").textContent = `${data.Data_Quality_Percentage}%`;
    document.getElementById("dqTotalRecords").textContent = data.Total_Records.toLocaleString();
    document.getElementById("dqMissing").textContent = data.Missing_Values;
    document.getElementById("dqDuplicates").textContent = data.Duplicate_Records;
    document.getElementById("dqOutliers").textContent = data.Abnormal_Sensor_Readings;

    const tbody = document.getElementById("dqPipelineTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.Pipeline_Stages.forEach(st => {
      const isAlert = st.status === "Alert";
      const badgeClass = isAlert ? "bg-amber-950 text-amber-400 border border-amber-800" : "bg-emerald-950 text-emerald-400 border border-emerald-800";

      const tr = document.createElement("tr");
      tr.className = "hover:bg-[#1e293b]/60 transition-colors";
      tr.innerHTML = `
        <td class="py-2.5 px-3 font-sans font-bold text-white">${st.stage}</td>
        <td class="py-2.5 px-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${badgeClass}">${st.status}</span>
        </td>
        <td class="py-2.5 px-3 text-gray-300 font-sans">${st.method || "Strict Validation"}</td>
        <td class="py-2.5 px-3 text-cyan-400">${(st.records_validated || st.records_normalized || st.records_fixed || st.matches || 27300).toLocaleString()} Records</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load data quality:", err);
  }
}

// ==========================================
// 12. DEMO SCENARIOS & LIVE TICK SIMULATION
// ==========================================
async function loadDemoScenario(scenarioName) {
  try {
    const res = await fetch(`/api/demo/scenario/${scenarioName}`);
    const data = await res.json();
    const m = data.machine_master;
    await viewMachineProfile(m.Machine_ID);
  } catch (err) {
    console.error("Failed to load demo scenario:", err);
  }
}

async function simulateLiveTelemetryTick() {
  try {
    await fetch("/api/telemetry/simulate-tick", { method: "POST" });
    // Refresh machine details if viewing
    if (!document.getElementById("view-machine-details").classList.contains("hidden")) {
      await viewMachineProfile(currentMachineId);
    }
  } catch (err) {
    console.error("Failed to simulate live telemetry:", err);
  }
}
