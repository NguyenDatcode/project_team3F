function loadAdminPage(url) {
    fetch(url)
        .then(res => res.text())
        .then(html => {
            document.getElementById("dynamicContent").innerHTML = html;
            if (url.includes("apartments")) initApartmentPage();
            if (url.includes("services")) initServicePage();
            if (url.includes("contracts")) initContractPage();
            if (url.includes("regulations")) initRegulationPage();
            if (url.includes("invoices")) initInvoicePage();
            if (url.includes("accounts")) initAccountPage();
            if (url.includes("reports")) initReportPage();
        });
}