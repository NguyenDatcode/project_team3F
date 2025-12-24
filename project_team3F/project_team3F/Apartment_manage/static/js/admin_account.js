let accountModal = null;
let accountDetailModal = null;

function initAccountPage() {
    const modalEl = document.getElementById("accountModal");
    const detailEl = document.getElementById("accountDetailModal");

    if (!modalEl || !detailEl) {
        console.error(" Không tìm thấy modal tài khoản");
        return;
    }

    accountModal = new bootstrap.Modal(modalEl);
    accountDetailModal = new bootstrap.Modal(detailEl);

    const form = document.getElementById("accountForm");
    if (form) {
        form.onsubmit = submitAccount;
    }

    loadAccounts();
}

function loadAccounts() {
    fetch("/admin/api/accounts")
        .then(res => res.json())
        .then(data => {
            const tb = document.getElementById("tblAccounts");
            tb.innerHTML = "";

            if (!data || data.length === 0) {
                tb.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            Chưa có tài khoản
                        </td>
                    </tr>`;
                return;
            }

            data.forEach(u => {
                tb.innerHTML += `
                <tr>
                    <td>${u.name}</td>
                    <td>${u.username}</td>
                    <td>${u.user_role}</td>
                    <td>${u.active ? "Hoạt động" : "Khoá"}</td>
                    <td>${u.created_at}</td>
                    <td>
                        <button class="btn btn-info btn-sm"
                            onclick='openViewAccountModal(${JSON.stringify(u)})'>
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-warning btn-sm"
                            onclick='openEditAccountModal(${JSON.stringify(u)})'>
                            Sửa
                        </button>
                        <button class="btn btn-secondary btn-sm"
                            onclick="resetPassword(${u.id})">
                            Reset PW
                        </button>
                    </td>
                </tr>`;
            });
        })
        .catch(err => {
            console.error(err);
            alert("Không load được danh sách tài khoản");
        });
}


function openAddAccountModal() {
    document.getElementById("accountForm").reset();
    document.getElementById("accountId").value = "";
    document.getElementById("username").disabled = false;
    document.getElementById("accountModalTitle").innerText = "Thêm tài khoản";

    accountModal.show();
}

function openEditAccountModal(u) {
    document.getElementById("accountModalTitle").innerText = "Cập nhật tài khoản";

    document.getElementById("accountId").value = u.id;
    document.getElementById("username").value = u.username;
    document.getElementById("username").disabled = true;
    document.getElementById("role").value = u.user_role;
    document.getElementById("active").checked = u.active;

    accountModal.show();
}

function openViewAccountModal(u) {
    document.getElementById("d_name").innerText = u.name;
    document.getElementById("d_username").innerText = u.username;
    document.getElementById("d_role").innerText = u.user_role;
    document.getElementById("d_active").innerText =
        u.active ? "Hoạt động" : "Khoá";
    document.getElementById("d_created").innerText = u.created_at;

    accountDetailModal.show();
}


function submitAccount(e) {
    e.preventDefault();

    const id = document.getElementById("accountId").value;

    const data = {
        name: document.getElementById("username").value,
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        user_role: document.getElementById("role").value,
        active: document.getElementById("active").checked
    };

    const url = id
        ? `/admin/api/accounts/${id}`
        : `/admin/api/accounts`;

    fetch(url, {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(res => {
            if (!res.ok) throw new Error("Lỗi lưu tài khoản");
            return res.json();
        })
        .then(() => {
            accountModal.hide();
            loadAccounts();
        })
        .catch(err => {
            console.error(err);
            alert("Không thể lưu tài khoản");
        });
}

/* ================= ACTION ================= */

function resetPassword(id) {
    if (!confirm("Reset mật khẩu về 123456?")) return;

    fetch(`/admin/api/accounts/${id}/reset`, { method: "POST" })
        .then(() => alert("Đã reset mật khẩu"));
}
