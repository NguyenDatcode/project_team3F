function loadAdminPage(url) {
    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error("404 Not Found");
            return res.text();
        })
        .then(html => {
            document.getElementById("dynamicContent").innerHTML = html;
        })
        .catch(err => {
            document.getElementById("dynamicContent").innerHTML =
                `<div class="alert alert-danger">Không load được trang</div>`;
            console.error(err);
        });
}
