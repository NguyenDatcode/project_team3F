// static/js/admin_types.js
document.addEventListener("DOMContentLoaded", function(){
  const tbody = document.querySelector("#tblTypes tbody");
  const modal = new bootstrap.Modal(document.getElementById("typeModal"));
  const form = document.getElementById("formType");

  async function load(){
    const res = await fetch("/admin/api/types");
    const data = await res.json();
    tbody.innerHTML = "";
    data.forEach((t, i)=>{
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${i+1}</td>
        <td>${t.name}</td>
        <td>${t.area_default}</td>
        <td>${t.base_price}</td>
        <td>
          <button class="btn btn-sm btn-primary btn-edit" data-id="${t.id}">Sửa</button>
          <button class="btn btn-sm btn-danger btn-del" data-id="${t.id}">Xóa</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
    attach();
  }

  function attach(){
    document.querySelectorAll(".btn-edit").forEach(b=>{
      b.onclick = async ()=>{
        const id = b.dataset.id;
        const res = await fetch("/admin/api/types");
        const list = await res.json();
        const t = list.find(x=>x.id==id);
        document.getElementById("typeId").value = t.id;
        document.getElementById("typeName").value = t.name;
        document.getElementById("typeArea").value = t.area_default;
        document.getElementById("typePrice").value = t.base_price;
        modal.show();
      }
    });
    document.querySelectorAll(".btn-del").forEach(b=>{
      b.onclick = async ()=>{
        if(!confirm("Xóa loại này?")) return;
        const id = b.dataset.id;
        const res = await fetch(`/admin/api/types/${id}`, { method: "DELETE" });
        const js = await res.json();
        if(js.success) load();
        else alert("Lỗi");
      }
    });
  }

  document.getElementById("btnAddType").addEventListener("click", ()=>{
    document.getElementById("typeId").value = "";
    document.getElementById("typeName").value = "";
    document.getElementById("typeArea").value = "";
    document.getElementById("typePrice").value = "";
    modal.show();
  });

  form.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const id = document.getElementById("typeId").value;
    const payload = {
      name: document.getElementById("typeName").value,
      area_default: parseFloat(document.getElementById("typeArea").value) || 0,
      base_price: parseFloat(document.getElementById("typePrice").value) || 0
    };
    if(!payload.name) return alert("Nhập tên");
    if(id){
      const res = await fetch(`/admin/api/types/${id}`, { method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
      const js = await res.json();
      if(js.success){ modal.hide(); load(); }
      else alert("Lỗi");
    } else {
      const res = await fetch(`/admin/api/types`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload) });
      const js = await res.json();
      if(js.success){ modal.hide(); load(); }
      else alert(js.error || "Lỗi");
    }
  });

  load();
});
