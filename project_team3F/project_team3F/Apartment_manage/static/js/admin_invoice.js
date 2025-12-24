////
////
////let invoiceModal;
////
////function initInvoicePage() {
////    invoiceModal = new bootstrap.Modal(
////        document.getElementById("invoiceModal")
////    );
////    loadInvoices();
////}
////
/////* ================= LOAD ================= */
////
////function loadInvoices() {
////    fetch("/admin/api/invoices")
////        .then(res => res.json())
////        .then(data => {
////            const tb = document.getElementById("tblInvoices");
////            tb.innerHTML = "";
////
////            data.forEach(i => {
////                tb.innerHTML += `
////                <tr>
////                    <td>${i.maHoaDon}</td>
////                    <td>${i.maHopDong}</td>
////                    <td>${i.thang}/${i.nam}</td>
////                    <td>${formatMoney(i.tongCong)}</td>
////                    <td>${i.status}</td>
////                    <td>
////                        <button class="btn btn-info btn-sm"
////                            onclick="viewInvoiceDetail(${i.id})">
////                            Xem
////                        </button>
////                        <button class="btn btn-secondary btn-sm"
////                            onclick="exportPDF(${i.id})">
////                            PDF
////                        </button>
////                    </td>
////                </tr>`;
////            });
////        });
////}
////
/////* ================= ACTION ================= */
////
////function viewInvoiceDetail(id) {
////    window.location.href = `/admin/invoices/${id}`;
////}
////
////function exportPDF(id) {
////    window.open(`/admin/api/invoices/${id}/pdf`, "_blank");
////}
////
////function openCreateInvoiceModal() {
////    invoiceModal.show();
////}
////
////function createInvoices() {
////    const month = document.getElementById("month").value;
////    const year = document.getElementById("year").value;
////
////    fetch("/admin/api/invoices/generate", {
////        method: "POST",
////        headers: { "Content-Type": "application/json" },
////        body: JSON.stringify({ thang: month, nam: year })
////    })
////    .then(() => {
////        invoiceModal.hide();
////        loadInvoices();
////    });
////}
////
//
///* ================= GLOBAL ================= */
//
//let invoiceModal = null;
//
///**
// * Được gọi sau khi invoice.html load
// */
//function initInvoicePage() {
//    const modalEl = document.getElementById("invoiceModal");
//    if (modalEl) {
//        invoiceModal = new bootstrap.Modal(modalEl);
//    }
//
//    loadInvoices();
//}
//
///**
// * Được gọi sau khi invoice_detail.html load
// */
//function initInvoiceDetailPage() {
//    const id = window.location.pathname.split("/").pop();
//    loadInvoiceDetail(id);
//}
//
///* ================= LOAD LIST ================= */
//
//function loadInvoices() {
//    fetch("/admin/api/invoices")
//        .then(res => res.json())
//        .then(data => {
//            const tb = document.getElementById("tblInvoices");
//            tb.innerHTML = "";
//
//            if (!data || data.length === 0) {
//                tb.innerHTML = `
//                    <tr>
//                        <td colspan="6" class="text-center text-muted">
//                            Chưa có hóa đơn
//                        </td>
//                    </tr>`;
//                return;
//            }
//
//            data.forEach(i => {
//                tb.innerHTML += `
//                <tr>
//                    <td>${i.maHoaDon}</td>
//                    <td>${i.hopDong}</td>
//                    <td>${i.thang}/${i.nam}</td>
//                    <td>${formatMoney(i.tongCong)}</td>
//                    <td>${i.status}</td>
//                    <td>
//                        <button class="btn btn-info btn-sm"
//                            onclick='openViewInvoiceModal(${JSON.stringify(i)})'>
//                            <i class="fas fa-eye"></i> Xem
//                        </button>
//                        <button class="btn btn-secondary btn-sm"
//                            onclick="exportPDF(${i.id})">
//                            PDF
//                        </button>
//                    </td>
//                </tr>`;
//            });
//        })
//        .catch(err => {
//            console.error(err);
//            alert("Không tải được danh sách hóa đơn");
//        });
//}
//
///* ================= DETAIL ================= */
//
//function loadInvoiceDetail(id) {
//    fetch(`/admin/api/invoices/${id}`)
//        .then(res => res.json())
//        .then(inv => {
//            document.getElementById("maHoaDon").innerText = inv.maHoaDon;
//            document.getElementById("maHopDong").innerText = inv.hopDong;
//            document.getElementById("thangNam").innerText = `${inv.thang}/${inv.nam}`;
//            document.getElementById("status").innerText = inv.status;
//            document.getElementById("tongCong").innerText =
//                formatMoney(inv.tongCong);
//
//            const tb = document.getElementById("tblInvoiceDetails");
//            tb.innerHTML = "";
//
//            inv.items.forEach(d => {
//                tb.innerHTML += `
//                <tr>
//                    <td>${d.tenDichVu}</td>
//                    <td>${d.moTa || ""}</td>
//                    <td>${formatMoney(d.donGia)}</td>
//                    <td>${d.soLuong}</td>
//                    <td>${formatMoney(d.thanhTien)}</td>
//                </tr>`;
//            });
//        })
//        .catch(err => {
//            console.error(err);
//            alert("Không tải được chi tiết hóa đơn");
//        });
//}
//
///* ================= ACTION ================= */
//
//function viewInvoiceDetail(id) {
//    window.location.href = `/admin/invoices/${id}`;
//}
//
//function exportPDF(id) {
//    window.open(`/admin/api/invoices/${id}/pdf`, "_blank");
//}
//
///* ================= CREATE ================= */
//
//function openCreateInvoiceModal() {
//    if (!invoiceModal) return;
//    invoiceModal.show();
//}
//
//function createInvoices() {
//    const month = document.getElementById("month").value;
//    const year = document.getElementById("year").value;
//
//    if (!month || !year) {
//        alert("Vui lòng nhập tháng và năm");
//        return;
//    }
//
//    fetch("/admin/api/invoices/generate", {
//        method: "POST",
//        headers: { "Content-Type": "application/json" },
//        body: JSON.stringify({
//            thang: Number(month),
//            nam: Number(year)
//        })
//    })
//        .then(res => {
//            if (!res.ok) throw new Error("Tạo hóa đơn thất bại");
//            return res.json();
//        })
//        .then(() => {
//            invoiceModal.hide();
//            loadInvoices();
//        })
//        .catch(err => {
//            console.error(err);
//            alert(err.message);
//        });
//}
//
///* ================= UTILS ================= */
//
//function formatMoney(v) {
//    if (v === null || v === undefined) return "0";
//    return Number(v).toLocaleString("vi-VN");
//}
//


let invoiceModal = null;
let invoiceDetailModal = null;

/**
 * Gọi sau khi invoice.html load vào dynamicContent
 */
function initInvoicePage() {

    const modalEl = document.getElementById("invoiceModal");
    const detailModalEl = document.getElementById("invoiceDetailModal");

    if (!modalEl || !detailModalEl) {
        console.error("Không tìm thấy modal hóa đơn");
        return;
    }

    invoiceModal = new bootstrap.Modal(modalEl);
    invoiceDetailModal = new bootstrap.Modal(detailModalEl);

    loadInvoices();
}

/* ================= LOAD ================= */

function loadInvoices() {
    fetch("/admin/api/invoices")
        .then(res => res.json())
        .then(data => {
            const tb = document.getElementById("tblInvoices");
            tb.innerHTML = "";

            if (!data || data.length === 0) {
                tb.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            Chưa có hóa đơn
                        </td>
                    </tr>`;
                return;
            }

            data.forEach(i => {
                tb.innerHTML += `
                <tr>
                    <td>${i.maHoaDon}</td>
                    <td>${i.hopDong}</td>
                    <td>${i.thang}/${i.nam}</td>
                    <td>${formatMoney(i.tongCong)}</td>
                    <td>${i.status}</td>
                    <td>
                        <button class="btn btn-info btn-sm"
                            onclick='openViewInvoiceModal(${JSON.stringify(i)})'>
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
            alert("Không load được hóa đơn");
        });
}

/* ================= VIEW MODAL ================= */

function openViewInvoiceModal(inv) {

    fetch(`/admin/api/invoices/${inv.id}`)
        .then(res => res.json())
        .then(d => {

            document.getElementById("d_maHoaDon").innerText = d.maHoaDon;
            document.getElementById("d_maHopDong").innerText = d.hopDong;
            document.getElementById("d_thangNam").innerText =
                `${d.thang}/${d.nam}`;
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
        .catch(err => {
            alert(err.message);
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
