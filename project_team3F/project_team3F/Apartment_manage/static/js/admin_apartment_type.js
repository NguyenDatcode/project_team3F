//async function loadTypes() {
//    let res = await fetch("/admin/api/apartment-type");
//    let data = await res.json();
//
//    let html = "";
//    data.forEach(t => {
//        html += `
//        <tr>
//            <td>${t.ten_loai}</td>
//            <td>${t.dien_tich}</td>
//            <td>${t.mo_ta}</td>
//            <td>
//                <button class="btn btn-warning btn-sm">Sửa</button>
//                <button class="btn btn-danger btn-sm">Xóa</button>
//            </td>
//        </tr>`;
//    });
//
//    document.getElementById("typeTable").innerHTML = html;
//}
//
//loadTypes();

function deleteType(id) {
    if (!confirm("Xóa loại căn hộ này?")) return;

    fetch(`/admin/api/apartment_type/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            location.reload();
        });
}
