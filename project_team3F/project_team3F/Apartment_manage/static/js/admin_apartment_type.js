function deleteType(id) {
    if (!confirm("Xóa loại căn hộ này?")) return;

    fetch(`/admin/api/apartment_type/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            location.reload();
        });
}
