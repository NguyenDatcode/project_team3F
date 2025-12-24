let contractModal = null;

function initContractPage() {
    const modalEl = document.getElementById("contractModal");
    contractModal = new bootstrap.Modal(modalEl);

    document.getElementById("contractForm").onsubmit = submitContract;
    loadContracts();
}

function loadContracts() {
    fetch("/admin/api/contracts")
        .then(res => res.json())
        .then(data => {
            const tb = document.getElementById("tblContracts");
            tb.innerHTML = "";

            data.forEach(c => {
                tb.innerHTML += `
                <tr>
                    <td>${c.maHopDong}</td>
                    <td>${c.tenant_name}</td>
                    <td>${c.apartment_title}</td>
                    <td>${c.giaThue}</td>
                    <td>${c.trangThai}</td>
                    <td>
                        <button class="btn btn-warning btn-sm"
                          onclick='openEditContract(${JSON.stringify(c)})'>Sửa</button>
                        <button class="btn btn-danger btn-sm"
                          onclick="deleteContract(${c.id})">Xóa</button>
                    </td>
                </tr>`;
            });
        });
}

/* ================= MODAL ================= */

function openAddContractModal() {
    document.getElementById("contractForm").reset();
    document.getElementById("contractId").value = "";
    document.getElementById("maHopDong").disabled = false;
    document.getElementById("contractModalTitle").innerText = "Thêm hợp đồng";
    contractModal.show();
}

function openEditContract(c) {
    document.getElementById("contractId").value = c.id;
    document.getElementById("maHopDong").value = c.maHopDong;
    document.getElementById("maHopDong").disabled = true;

    document.querySelector("[name=tenant_name]").value = c.tenant_name;
    document.querySelector("[name=thoiHan]").value = c.thoiHan;
    document.querySelector("[name=giaThue]").value = c.giaThue;
    document.querySelector("[name=tienCoc]").value = c.tienCoc;
    document.querySelector("[name=ngayBatDau]").value = c.ngayBatDau;
    document.querySelector("[name=apartment_id]").value = c.apartment_id;
    document.querySelector("[name=trangThai]").value = c.trangThai;

    document.getElementById("contractModalTitle").innerText = "Sửa hợp đồng";
    contractModal.show();
}

/* ================= SUBMIT ================= */
//
//function submitContract(e) {
//    e.preventDefault();
//
//    const id = document.getElementById("contractId").value;
//    const formData = new FormData(e.target);
//
//    const url = id
//        ? `/admin/api/contracts/${id}`
//        : `/admin/api/contracts`;
//
//    fetch(url, {
//        method: id ? "PUT" : "POST",
//        body: formData
//    }).then(() => {
//        contractModal.hide();
//        loadContracts();
//    });
//}

function submitContract(e) {
    e.preventDefault();

    const id = document.getElementById("contractId").value;
    const formData = new FormData(e.target);

    const url = id
        ? `/admin/api/contracts/${id}`
        : `/admin/api/contracts`;

    fetch(url, {
    method: id ? "PUT" : "POST",
    body: formData
         })
         .then(res => {
             if (!res.ok) throw new Error("HTTP " + res.status);
             return res.json();
         })
         .then(data => {
             if (!data.success) {
                 alert(data.message || "Lỗi khi lưu hợp đồng");
                 return;
             }
             contractModal.hide();
             loadContracts();
         })
         .catch(err => {
             console.error(err);
             alert("Không thể lưu hợp đồng");
         });
}


function deleteContract(id) {
    if (!confirm("Xóa hợp đồng này?")) return;
    fetch(`/admin/api/contracts/${id}`, { method: "DELETE" })
        .then(() => loadContracts());
}
