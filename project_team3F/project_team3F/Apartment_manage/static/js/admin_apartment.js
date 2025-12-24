let apartmentModal = null;
function initApartmentPage() {
    const modalEl = document.getElementById("apartmentModal");

    if (!modalEl) {
        console.error(" Không tìm thấy apartmentModal");
        return;
    }

    apartmentModal = new bootstrap.Modal(modalEl);

    const form = document.getElementById("apartmentForm");
    if (form) {
        form.onsubmit = submitApartment;
    }

    loadApartments();
}

/* ================= MODAL ================= */

function openAddModal() {
    if (!apartmentModal) {
        alert("Modal chưa sẵn sàng");
        return;
    }

    document.getElementById("modalTitle").innerText = "Thêm căn hộ";
    document.getElementById("apartmentForm").reset();
    document.getElementById("apartmentId").value = "";

    apartmentModal.show();
}

function openEditModal(apartment) {
    if (!apartmentModal) {
        alert("Modal chưa sẵn sàng");
        return;
    }

    document.getElementById("modalTitle").innerText = "Sửa căn hộ";

    document.getElementById("apartmentId").value = apartment.id;
    document.getElementById("title").value = apartment.title;
    document.getElementById("price").value = apartment.price;
    document.getElementById("area").value = apartment.area;
    document.getElementById("type_id").value = apartment.type_id;
    document.getElementById("description_short").value = apartment.description_short || "";

    apartmentModal.show();
}

/* ================= CRUD ================= */

function loadApartments() {
    fetch("/admin/api/apartments")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("tblApartments");
            tbody.innerHTML = "";

            data.forEach(a => {
                tbody.innerHTML += `
                <tr>
                    <td>${a.id}</td>
                    <td>${a.title}</td>
                    <td>${a.price} Triệu</td>
                    <td>${a.type_name}</td>
                    <td>${a.status}</td>
                    <td>
                        ${a.image_url ? `<img src="${a.image_url}" width="80">` : ""}
                    </td>
                    <td>
                        <button class="btn btn-sm btn-warning"
                            onclick='openEditModal(${JSON.stringify(a)})'>Sửa</button>
                        <button class="btn btn-sm btn-danger"
                            onclick="deleteApartment(${a.id})">Xóa</button>
                    </td>
                </tr>
                `;
            });
        });
}

function submitApartment(e) {
    e.preventDefault();

    const form = document.getElementById("apartmentForm");
    const formData = new FormData(form);

    // VALIDATE CLIENT
    if (!formData.get("title")) {
        alert("Tên căn hộ không được rỗng");
        return;
    }

    if (formData.get("price") <= 0) {
        alert("Giá phải > 0");
        return;
    }

    const id = document.getElementById("apartmentId").value;
    const url = id
        ? `/admin/api/apartments/${id}`
        : `/admin/api/apartments`;

    fetch(url, {
        method: id ? "PUT" : "POST",
        body: formData
    })
    .then(res => {
        if (!res.ok) throw new Error("Server error");
        return res.json();
    })
    .then(() => {
        apartmentModal.hide();
        loadApartments();
    })
    .catch(err => {
        alert("Lỗi khi lưu căn hộ");
        console.error(err);
    });
}


function deleteApartment(id) {
    if (!confirm("Xóa căn hộ này?")) return;

    fetch(`/admin/api/apartments/${id}`, { method: "DELETE" })
        .then(() => loadApartments());
}



