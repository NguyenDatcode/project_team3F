let serviceModal;

function initServicePage() {
    serviceModal = new bootstrap.Modal(
        document.getElementById("serviceModal")
    );
    document.getElementById("serviceForm").onsubmit = submitService;
    loadServices();
}


function loadServices() {
    fetch("/admin/api/services")
        .then(res => res.json())
        .then(data => {
            const tb = document.getElementById("tblServices");
            tb.innerHTML = "";
            data.forEach(s => {
                tb.innerHTML += `
                <tr>
                    <td>${s.maDichVu}</td>
                    <td>${s.tenDichVu}</td>
                    <td>${s.donGia}</td>
                    <td>${s.donViTinh}</td>
                    <td>${s.loaiTinhPhi}</td>
                    <td>
                        <button class="btn btn-warning btn-sm"
                          onclick='openEditService(${JSON.stringify(s)})'>Sửa</button>
                        <button class="btn btn-danger btn-sm"
                          onclick="deleteService(${s.id})">Xóa</button>
                    </td>
                </tr>`;
            });
        });
}

/* ===== MODAL ===== */
function openAddServiceModal() {
    document.getElementById("serviceForm").reset();
    document.getElementById("serviceId").value = "";
    document.getElementById("serviceModalTitle").innerText = "Thêm dịch vụ";
    serviceModal.show();
}

function openEditService(s) {
    document.getElementById("serviceId").value = s.id;
    document.getElementById("maDichVu").value = s.maDichVu;
    document.getElementById("maDichVu").disabled = true;
    document.querySelector("[name=tenDichVu]").value = s.tenDichVu;
    document.querySelector("[name=donGia]").value = s.donGia;
    document.querySelector("[name=donViTinh]").value = s.donViTinh;
    document.querySelector("[name=loaiTinhPhi]").value = s.loaiTinhPhi;
    serviceModal.show();
}

/* ===== SUBMIT ===== */
function submitService(e) {
    e.preventDefault();

    const id = document.getElementById("serviceId").value;
    const formData = new FormData(e.target);

    const url = id
        ? `/admin/api/services/${id}`
        : `/admin/api/services`;

    fetch(url, {
        method: id ? "PUT" : "POST",
        body: formData
    }).then(() => {
        serviceModal.hide();
        loadServices();
    });
}

function deleteService(id) {
    if (!confirm("Xóa dịch vụ này?")) return;
    fetch(`/admin/api/services/${id}`, { method: "DELETE" })
        .then(() => loadServices());
}
