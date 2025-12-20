let regulationModal = null;
let regulationDetailModal;

/**
 * Được gọi SAU KHI regulation.html được load vào dynamicContent
 */
function initRegulationPage() {
    const modalEl = document.getElementById("regulationModal");
    const DetailModal=document.getElementById("regulationDetailModal");
    if (!modalEl || !DetailModal) {
        console.error(" Không tìm thấy regulationModal");
        return;
    }

    regulationModal = new bootstrap.Modal(modalEl);
    regulationDetailModal = new bootstrap.Modal(
        document.getElementById("regulationDetailModal")
    );

    const form = document.getElementById("regulationForm");
    if (form) {
        form.onsubmit = submitRegulation;
    }

    loadRegulations();
}


/* ================= LOAD DATA ================= */

function loadRegulations() {
    fetch("/admin/api/regulations")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("tblRegulations");
            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center text-muted">
                            Chưa có quy định nào
                        </td>
                    </tr>`;
                return;
            }

            data.forEach(r => {
                const hieuLuc = r.ngayKetThuc
                    ? `${r.ngayBatDau} → ${r.ngayKetThuc}`
                    : `${r.ngayBatDau} → Hiện tại`;

                tbody.innerHTML += `
                    <tr>
                        <td>${r.maQuyDinh}</td>
                        <td>${r.tenQuyDinh}</td>
                        <td>${formatMoney(r.giaDien)}</td>
                        <td>${formatMoney(r.giaNuoc)}</td>
                        <td>${formatMoney(r.phiDichVu)}</td>
                        <td>${r.soNguoiToiDa}</td>
                        <td>${hieuLuc}</td>
                        <td>
                            <button class="btn btn-sm btn-warning"
                                onclick='openEditRegulation(${JSON.stringify(r)})'>
                                Sửa
                            </button>
                            <button class="btn btn-sm btn-danger"
                                onclick="deleteRegulation(${r.id})">
                                Xóa
                            </button>
                        </td>
                        <td>
                            <button class="btn btn-info btn-sm"
                                onclick='openViewRegulationModal(${JSON.stringify(r)})'>
                                <i class="fas fa-eye"></i> Xem
                            </button>
                        </td>

                    </tr>
                `;
            });
        })
        .catch(err => {
            console.error(err);
            alert("Không load được danh sách quy định");
        });
}

/* ================= MODAL ================= */

function openAddRegulationModal() {
    document.getElementById("regulationForm").reset();
    document.getElementById("regulationId").value = "";
    document.getElementById("regulationModalTitle").innerText = "Thêm quy định mới";

    regulationModal.show();
}

function openEditRegulation(r) {
    document.getElementById("regulationModalTitle").innerText = "Cập nhật quy định";

    document.getElementById("regulationId").value = r.id;

    document.querySelector("[name=maQuyDinh]").value = r.maQuyDinh;
    document.querySelector("[name=tenQuyDinh]").value = r.tenQuyDinh;
    document.querySelector("[name=giaDien]").value = r.giaDien;
    document.querySelector("[name=giaNuoc]").value = r.giaNuoc;
    document.querySelector("[name=phiDichVu]").value = r.phiDichVu;
    document.querySelector("[name=soNguoiToiDa]").value = r.soNguoiToiDa;
    document.querySelector("[name=phiTreHan]").value = r.phiTreHan;

    document.querySelector("[name=ngayBatDau]").value = r.ngayBatDau;
    document.querySelector("[name=ngayKetThuc]").value = r.ngayKetThuc || "";
    document.querySelector("[name=ghiChu]").value = r.ghiChu || "";

    regulationModal.show();
}

/* ================= SUBMIT ================= */

function submitRegulation(e) {
    e.preventDefault();

    const id = document.getElementById("regulationId").value;
    const form = e.target;
    const formData = new FormData(form);

    // ===== CLIENT VALIDATION =====
    const giaDien = Number(formData.get("giaDien"));
    const giaNuoc = Number(formData.get("giaNuoc"));
    const ngayBatDau = formData.get("ngayBatDau");
    const ngayKetThuc = formData.get("ngayKetThuc");

    if (giaDien <= 0 || giaNuoc <= 0) {
        alert("Giá điện và giá nước phải > 0");
        return;
    }

    if (ngayKetThuc && ngayKetThuc < ngayBatDau) {
        alert("Ngày kết thúc phải >= ngày bắt đầu");
        return;
    }

    const url = id
        ? `/admin/api/regulations/${id}`
        : `/admin/api/regulations`;

    fetch(url, {
        method: id ? "PUT" : "POST",
        body: formData
    })
        .then(res => {
            if (!res.ok) throw new Error("Lỗi khi lưu quy định");
            return res.json();
        })
        .then(() => {
            regulationModal.hide();
            loadRegulations();
        })
        .catch(err => {
            console.error(err);
            alert("Không thể lưu quy định");
        });
}

/* ================= DELETE ================= */

function deleteRegulation(id) {
    if (!confirm("Xóa quy định này?")) return;

    fetch(`/admin/api/regulations/${id}`, {
        method: "DELETE"
    })
        .then(res => {
            if (!res.ok) throw new Error("Xóa thất bại");
            loadRegulations();
        })
        .catch(err => {
            console.error(err);
            alert("Không thể xóa quy định");
        });
}

/* ================= UTILS ================= */
/*HÀM ĐỊNH DẠNG LẠI số tiền trên giao diện*/
function formatMoney(v) {
    if (v === null || v === undefined) return "";
    return Number(v).toLocaleString("vi-VN");
}



function openViewRegulationModal(r) {
    document.getElementById("d_maQuyDinh").innerText = r.maQuyDinh;
    document.getElementById("d_tenQuyDinh").innerText = r.tenQuyDinh;
    document.getElementById("d_giaDien").innerText = formatMoney(r.giaDien) + " đ/kWh";
    document.getElementById("d_giaNuoc").innerText = formatMoney(r.giaNuoc) + " đ/m³";
    document.getElementById("d_phiDichVu").innerText = formatMoney(r.phiDichVu) + " đ";
    document.getElementById("d_soNguoiToiDa").innerText = r.soNguoiToiDa + " người";
    document.getElementById("d_phiTreHan").innerText = formatMoney(r.phiTreHan) + " đ/ngày";

    document.getElementById("d_hieuLuc").innerText =
        r.ngayBatDau + " → " + (r.ngayKetThuc || "Không xác định");

    document.getElementById("d_ghiChu").innerText =
        r.ghiChu || "Không có";

    regulationDetailModal.show();
}

