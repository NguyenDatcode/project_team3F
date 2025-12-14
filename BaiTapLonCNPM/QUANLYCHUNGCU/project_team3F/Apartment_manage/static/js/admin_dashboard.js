function loadAdminPage() {
    fetch('/admin/apartments')
        .then(res => {
            console.log(res);
            if (!res.ok) throw new Error("404 Not Found");
            return res.text();
        })
        .then(html => {
            document.getElementById("dynamicContent").innerHTML = html;

//            if ("/admin/apartments".includes("apartments")) {
//                loadApartments();
//            }

              if (typeof initApartmentPage === "function") {
                initApartmentPage();
            }
        })
        .catch(err => {
            document.getElementById("dynamicContent").innerHTML =
                `<div class="alert alert-danger">Không load được trang</div>`;
            console.error(err);
        });
}

