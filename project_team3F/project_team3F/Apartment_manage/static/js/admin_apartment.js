

document.addEventListener("DOMContentLoaded", () => {
    loadApartments();
});

function loadApartments() {
    fetch("/admin/api/apartments")
        .then(res => res.json())
        .then(data => {
            let html = "";
            data.forEach((ap, index) => {
                html += `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${ap.title}</td>
                        <td>${ap.price.toLocaleString()}đ</td>
                        <td>${ap.type_name}</td>
                        <td>${statusLabel(ap.status)}</td>
                        <td class="text-center">
                            <button class="btn btn-sm btn-warning" onclick="editApartment(${ap.id})">Sửa</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteApartment(${ap.id})">Xoá</button>
                        </td>
                    </tr>
                `;
            });

            document.querySelector("#tblBody").innerHTML = html;
        });
}

function statusLabel(s) {
    switch (s) {
        case "available": return `<span class="badge bg-success">Trống</span>`;
        case "rented": return `<span class="badge bg-secondary">Đang thuê</span>`;
        case "maintenance": return `<span class="badge bg-warning text-dark">Sửa chữa</span>`;
    }
}
