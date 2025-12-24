let invoiceModal = null;
let invoiceDetailModal = null;

function initInvoicePage() {
    const modalEl = document.getElementById("invoiceModal");
    const detailModalEl = document.getElementById("invoiceDetailModal");

    if (!modalEl || !detailModalEl) {
        console.error("Không tìm thấy modal hóa đơn");
        return;
    }

    invoiceModal = new bootstrap.Modal(modalEl);
    invoiceDetailModal = new bootstrap.Modal(detailModalEl);

    initFilters();
    loadInvoices();
}

/* ================= FILTER ================= */

function initFilters() {
    const monthSelect = document.getElementById("filterMonth");
    const yearSelect = document.getElementById("filterYear");
    const statusSelect = document.getElementById("filterStatus");

    if (!monthSelect || !yearSelect || !statusSelect) return;

    // Tháng
    monthSelect.innerHTML = `<option value="">-- Tháng --</option>`;
    for (let m = 1; m <= 12; m++) {
        monthSelect.innerHTML += `<option value="${m}">Tháng ${m}</option>`;
    }

    // Năm (±5 năm)
    yearSelect.innerHTML = `<option value="">-- Năm --</option>`;
    const currentYear = new Date().getFullYear();
    for (let y = currentYear - 5; y <= currentYear + 1; y++) {
        yearSelect.innerHTML += `<option value="${y}">${y}</option>`;
    }

    // Gắn sự kiện
    monthSelect.addEventListener("change", loadInvoices);
    yearSelect.addEventListener("change", loadInvoices);
    statusSelect.addEventListener("change", loadInvoices);
}

/* ================= LOAD INVOICES ================= */

function loadInvoices() {
    fetch("/admin/api/invoices")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("tblInvoices");
            tbody.innerHTML = "";

            if (!Array.isArray(data) || data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            Chưa có hóa đơn
                        </td>
                    </tr>`;
                return;
            }

            // Lấy filter
            const fMonth = document.getElementById("filterMonth").value;
            const fYear = document.getElementById("filterYear").value;
            const fStatus = document.getElementById("filterStatus").value;

            // Lọc
            const filtered = data.filter(i => {
                if (fMonth && Number(i.thang) !== Number(fMonth)) return false;
                if (fYear && Number(i.nam) !== Number(fYear)) return false;
                if (fStatus && i.status !== fStatus) return false;
                return true;
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            Không có hóa đơn phù hợp
                        </td>
                    </tr>`;
                return;
            }

            // Render
            filtered.forEach(i => {
                const isPaid = i.status === "Đã thanh toán";

                tbody.innerHTML += `
                <tr>
                    <td>${i.maHoaDon}</td>
                    <td>${i.hopDong || ""}</td>
                    <td>${i.thang}/${i.nam}</td>
                    <td>${formatMoney(i.tongCong)}</td>
                    <td>
                        <span class="badge ${isPaid ? "bg-success" : "bg-warning"}">
                            ${i.status}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-info btn-sm"
                            onclick="openViewInvoiceModal(${i.id})">
                            <i class="fas fa-eye"></i> Xem
                        </button>
                        <button class="btn btn-secondary btn-sm"
                            onclick="exportPDF(${i.id})">
                            PDF
                        </button>
                    </td>
                </tr>`;
            });
        })
        .catch(err => {
            console.error(err);
            alert("Không load được danh sách hóa đơn");
        });
}

/* ================= VIEW DETAIL ================= */

function openViewInvoiceModal(id) {
    fetch(`/admin/api/invoices/${id}`)
        .then(res => res.json())
        .then(d => {
            document.getElementById("d_maHoaDon").innerText = d.maHoaDon;
            document.getElementById("d_maHopDong").innerText = d.hopDong;
            document.getElementById("d_thangNam").innerText = `${d.thang}/${d.nam}`;
            document.getElementById("d_status").innerText = d.status;
            document.getElementById("d_tongCong").innerText =
                formatMoney(d.tongCong) + " đ";

            const tbody = document.getElementById("tblInvoiceDetailBody");
            tbody.innerHTML = "";

            d.items.forEach(it => {
                tbody.innerHTML += `
                    <tr>
                        <td>${it.tenDichVu}</td>
                        <td>${it.moTa || ""}</td>
                        <td>${formatMoney(it.donGia)}</td>
                        <td>${it.soLuong}</td>
                        <td>${formatMoney(it.thanhTien)}</td>
                    </tr>`;
            });

            invoiceDetailModal.show();
        });
}

/* ================= PDF ================= */

function exportPDF(id) {
    window.open(`/admin/api/invoices/${id}/pdf`, "_blank");
}

/* ================= UTILS ================= */

function formatMoney(v) {
    if (v === null || v === undefined) return "";
    return Number(v).toLocaleString("vi-VN");
}

/* ================= VIEW DETAIL ================= */

function openViewInvoiceModal(invoiceId) {
    fetch(`/admin/api/invoices/${invoiceId}`)
        .then(res => res.json())
        .then(d => {
            document.getElementById("d_maHoaDon").innerText = d.maHoaDon;
            document.getElementById("d_maHopDong").innerText = d.hopDong;
            document.getElementById("d_thangNam").innerText = `${d.thang}/${d.nam}`;
            document.getElementById("d_status").innerText = d.status;
            document.getElementById("d_tongCong").innerText =
                formatMoney(d.tongCong) + " đ";

            const tbody = document.getElementById("tblInvoiceDetailBody");
            tbody.innerHTML = "";

            d.items.forEach(it => {
                tbody.innerHTML += `
                    <tr>
                        <td>${it.tenDichVu}</td>
                        <td>${it.moTa || ""}</td>
                        <td>${formatMoney(it.donGia)}</td>
                        <td>${it.soLuong}</td>
                        <td>${formatMoney(it.thanhTien)}</td>
                    </tr>`;
            });

            invoiceDetailModal.show();
        })
        .catch(err => {
            console.error(err);
            alert("Không load được chi tiết hóa đơn");
        });
}

/* ================= CREATE ================= */

function openCreateInvoiceModal() {
    invoiceModal.show();
}

function createInvoices() {
    const month = document.getElementById("month").value;
    const year = document.getElementById("year").value;

    if (!month || !year) {
        alert("Vui lòng nhập tháng và năm");
        return;
    }

    fetch("/admin/api/invoices/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            thang: Number(month),
            nam: Number(year)
        })
    })
        .then(res => {
            if (!res.ok) throw new Error("Tạo hóa đơn thất bại");
            return res.json();
        })
        .then(() => {
            invoiceModal.hide();
            loadInvoices();
        })
        .catch(err => alert(err.message));
}

/* ================= PDF ================= */

function exportPDF(id) {
    window.open(`/admin/api/invoices/${id}/pdf`, "_blank");
}

/* ================= UTILS ================= */

function formatMoney(v) {
    if (v === null || v === undefined) return "";
    return Number(v).toLocaleString("vi-VN");
}
