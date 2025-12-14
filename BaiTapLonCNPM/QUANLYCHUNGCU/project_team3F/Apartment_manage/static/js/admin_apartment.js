////const modal = new bootstrap.Modal(document.getElementById('apartmentModal'));
////
////function loadApartments() {
////    fetch('/admin/api/apartments', {
////        headers: { 'Accept': 'application/json' }
////    })
////    .then(res => res.json())
////    .then(data => {
////        let html = '';
////        data.forEach((a, i) => {
////            html += `
////                <tr>
////                    <td>${i + 1}</td>
////                    <td>${a.title}</td>
////                    <td>${a.price}</td>
////                    <td>${a.type}</td>
////                    <td>${a.status}</td>
////                    <td>
////                        <button class="btn btn-sm btn-danger" onclick="delApartment(${a.id})">
////                            Xóa
////                        </button>
////                    </td>
////                </tr>
////            `;
////        });
////        document.getElementById('tblApartments').innerHTML = html;
////    });
////}
////
////function openAddModal() {
////    document.getElementById('formApartment').reset();
////    document.getElementById('apId').value = '';
////    modal.show();
////}
////
////document.getElementById('formApartment').onsubmit = function (e) {
////    e.preventDefault();
////
////    fetch('/admin/apartments', {
////        method: 'POST',
////        headers: { 'Content-Type': 'application/json' },
////        body: JSON.stringify({
////            title: title.value,
////            price: price.value,
////            status: status.value,
////            apartment_type_id: apartment_type_id.value
////        })
////    }).then(() => {
////        modal.hide();
////        loadApartments();
////    });
////};
////
////function delApartment(id) {
////    if (!confirm('Xóa căn hộ này?')) return;
////
////    fetch(`/admin/apartments/${id}`, {
////        method: 'DELETE'
////    }).then(() => loadApartments());
////}
////
////loadApartments();
//
//
//document.addEventListener("DOMContentLoaded", loadApartments);
//
//function loadApartments() {
//    fetch("/admin/api/apartments")
//        .then(res => res.json())
//        .then(data => {
//            const tbody = document.getElementById("tblApartments");
//            tbody.innerHTML = "";
//
//            data.forEach((a, i) => {
//                tbody.innerHTML += `
//                <tr>
//                    <td>${i + 1}</td>
//                    <td>${a.title}</td>
//                    <td>${a.price}</td>
//                    <td>${a.type_name}</td>
//                    <td>${a.status}</td>
//                    <td>
//                        <button class="btn btn-sm btn-warning">Sửa</button>
//                        <button class="btn btn-sm btn-danger">Xóa</button>
//                    </td>
//                </tr>`;
//            });
//        })
//        .catch(err => console.error(err));
//}


document.addEventListener("DOMContentLoaded", loadApartments);

function loadApartments() {
    fetch("/admin/api/apartments")
        .then(res => res.json())
        .then(data => {
            let rows = "";
            data.forEach((a, i) => {
                rows += `
                <tr>
                    <td>${i + 1}</td>
                    <td>${a.title}</td>
                    <td>${a.price}</td>
                    <td>${a.type_name}</td>
                    <td>${a.status}</td>
                    <td>
                        <button class="btn btn-danger btn-sm"
                            onclick="deleteApartment(${a.id})">Xóa</button>
                    </td>
                </tr>`;
            });
            document.getElementById("tblApartments").innerHTML = rows;
        });
}

function deleteApartment(id) {
    if (!confirm("Xóa căn hộ?")) return;
    fetch(`/admin/api/apartments/${id}`, { method: "DELETE" })
        .then(() => loadApartments());
}
