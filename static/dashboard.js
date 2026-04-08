async function loadDashboard() {

    const res = await fetch("/api/incidents");
    let data = await res.json();

    // ---------------- FILTER ----------------
    const filter = document.getElementById("filter").value;

    if (filter !== "all") {
        data = data.filter(i =>
            (i.severity || "").toLowerCase() === filter
        );
    }

    // ---------------- KPI ----------------
    let total = data.length;
    let high = 0, medium = 0, low = 0;

    let equipmentCount = {};
    let departmentCount = {};
    let locationCount = {};

    data.forEach(i => {

        let s = (i.severity || "").toLowerCase();

        if (s === "high") high++;
        else if (s === "medium") medium++;
        else low++;

        if (i.equipment) {
            equipmentCount[i.equipment] = (equipmentCount[i.equipment] || 0) + 1;
        }

        if (i.department) {
            departmentCount[i.department] = (departmentCount[i.department] || 0) + 1;
        }

        if (i.location_or_unit) {
            locationCount[i.location_or_unit] = (locationCount[i.location_or_unit] || 0) + 1;
        }
    });

    document.getElementById("total").innerText = total;
    document.getElementById("high").innerText = high;
    document.getElementById("medium").innerText = medium;
    document.getElementById("low").innerText = low;

    // ---------------- TOP EQUIPMENT ----------------
    let topEquipment = Object.entries(equipmentCount)
        .sort((a, b) => b[1] - a[1])[0]?.[0] || "-";

    document.getElementById("topEquipment").innerText = topEquipment;

    // ---------------- TOP DEPARTMENT ----------------
    let topDept = Object.entries(departmentCount)
        .sort((a, b) => b[1] - a[1])[0]?.[0] || "-";

    document.getElementById("topDept").innerText = topDept;

    // ---------------- TREND ENGINE ----------------
    let trend = "✅ Stable operations";

    if (high > medium && high > low) {
        trend = "🚨 Critical: High severity incidents rising";
    } else if (medium > high) {
        trend = "⚠️ Warning: Medium incidents increasing";
    } else if (low > high && low > medium) {
        trend = "🟢 Mostly low-risk incidents";
    }

    document.getElementById("trendText").innerText = trend;

    // ---------------- CHARTS ----------------
    renderCharts(high, medium, low, equipmentCount);

    // ---------------- TABLE ----------------
    renderTable(data);
}


// ---------------- CHARTS ----------------
let severityChart, equipmentChart;

function renderCharts(high, medium, low, equipmentCount) {

    // Destroy previous charts
    if (severityChart) severityChart.destroy();
    if (equipmentChart) equipmentChart.destroy();

    // Severity Bar
    const ctx1 = document.getElementById("severityChart").getContext("2d");
    severityChart = new Chart(ctx1, {
        type: "bar",
        data: {
            labels: ["High", "Medium", "Low"],
            datasets: [{
                label: "Incidents",
                data: [high, medium, low]
            }]
        }
    });

    // Equipment Pie
    const ctx2 = document.getElementById("equipmentChart").getContext("2d");

    const labels = Object.keys(equipmentCount);
    const values = Object.values(equipmentCount);

    equipmentChart = new Chart(ctx2, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                data: values
            }]
        }
    });
}


// ---------------- TABLE ----------------
function renderTable(data) {

    const table = document.getElementById("incidentTable");
    table.innerHTML = "";

    data = data.reverse().slice(0, 10);

    data.forEach(i => {

        const row = `
        <tr>
            <td>${i.equipment || "-"}</td>
            <td>${i.department || "-"}</td>
            <td>${i.location_or_unit || "-"}</td>
            <td>${i.incident_summary || "-"}</td>
            <td class="severity-${(i.severity || "").toLowerCase()}">${i.severity}</td>
           
        </tr>
        `;

        table.innerHTML += row;
    });
}


// ---------------- AUTO REFRESH ----------------
setInterval(loadDashboard, 5000);
loadDashboard();