function getSeverityClass(severity) {
    if (!severity) return "";

    severity = severity.toLowerCase();

    if (severity === "high") return "severity-high";
    if (severity === "medium") return "severity-medium";
    return "severity-low";
}
async function loadIncidents() {
    const res = await fetch('/api/incidents');
    const data = await res.json();

    const table = document.getElementById('incidentTable');
    table.innerHTML = '';

    data.reverse().forEach(i => {
        table.innerHTML += `
            <tr>
                <td>${i.equipment}</td>
                <td>${i.incident_summary}</td>
                <td>${i.location_or_unit}</td>
                <td>${i.severity}</td>
                <td>${i.incident_date}</td>
                <td>${i.incident_time}</td>
            </tr>
        `;
    });
}

async function loadStats() {
    const res = await fetch('/api/stats');
    const data = await res.json();

    document.getElementById('total').innerText = data.total;
    document.getElementById('high').innerText = data.high;
}

setInterval(() => {
    loadIncidents();
    loadStats();
}, 3000);

loadIncidents();
loadStats();