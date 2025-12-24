let aptChartInstance = null;

document.addEventListener("DOMContentLoaded", initReportPage);

function initReportPage() {
    loadApartmentStatus();
    loadRevenue();
    loadExpiringContracts();

    const chartType = document.getElementById("chartType");
    if (chartType) {
        chartType.addEventListener("change", loadApartmentStatus);
    }

    const yearInput = document.getElementById("yearInput");
    if (yearInput) {
        yearInput.addEventListener("change", loadRevenue);
    }
}

/* ================== TÌNH TRẠNG PHÒNG ================== */
function loadApartmentStatus() {
    const chartTypeEl = document.getElementById("chartType");
    if (!chartTypeEl) return;

    const type = chartTypeEl.value;

    fetch("/admin/api/reports/apartment-status")
        .then(res => res.json())
        .then(data => {
            const canvas = document.getElementById("aptChart");
            if (!canvas) return;

            const ctx = canvas.getContext("2d");

            if (aptChartInstance) {
                aptChartInstance.destroy();
            }

            aptChartInstance = new Chart(ctx, {
                type: type,
                data: {
                    labels: ["Đang thuê", "Trống"],
                    datasets: [{
                        data: [data.dangThue, data.trong],
                        backgroundColor: ["#0d6efd", "#adb5bd"]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        })
        .catch(err => console.error("Apartment chart error:", err));
}

/* ================== DOANH THU ================== */
let revenueChart = null;

function loadRevenue() {
    fetch("/admin/api/reports/revenue")
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById("revenueChart");
            if (!ctx) return;

            if (revenueChart) revenueChart.destroy();

            revenueChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: "Doanh thu",
                        data: data.values,
                        backgroundColor: "#198754"
                    }]
                }
            });
        });
}


/* ================== HỢP ĐỒNG SẮP HẾT HẠN ================== */
function loadExpiringContracts() {
    fetch("/admin/api/reports/contracts-expiring")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("expiringContracts");
            if (!tbody) return;

            tbody.innerHTML = "";

            if (!Array.isArray(data) || data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-muted">
                            Không có hợp đồng sắp hết hạn
                        </td>
                    </tr>`;
                return;
            }

            data.forEach(c => {
                tbody.innerHTML += `
                    <tr>
                        <td>${c.maHopDong}</td>
                        <td>${c.tenant}</td>
                        <td>${c.ngayBatDau}</td>
                        <td>${c.days_left} ngày</td>
                    </tr>
                `;
            });
        })
        .catch(err => console.error("Expiring contracts error:", err));
}

