import hashlib
import json
import os
from datetime import date, datetime, timedelta

from flask import render_template, request, redirect, url_for, flash, jsonify, Blueprint, send_file
from flask_login import logout_user, login_user, login_required
from sqlalchemy import func

from Apartment_manage import dao, login, create_app, db
from Apartment_manage.dao import add_user
from Apartment_manage.models import User, UserRole, Contract, Invoice, Regulation, Apartment, ContractStatus

# from Apartment_manage.admin import admin_bp


app = create_app()

@app.route("/rule")
def load_rule():
    return render_template("rule.html")

# ============================
# REGISTER
# ============================
@app.route('/register', methods=['GET'])
def load_register():
    return render_template('register.html')


def read_json(filename):
    path = os.path.join(app.root_path, "templates", "Data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ================= USER LOADER =================
@login.user_loader
def load_user(uid):
    return dao.get_user_by_id(uid)

@app.route("/index")
def index():
    notifications = read_json("notify.json")
    bills = read_json("pay.json")
    return render_template("index.html", notifications=notifications, bills=bills)

@app.route("/extension/<extension_name>")
def load_extension(extension_name):
    if extension_name == "notify_extension":
        notifications = read_json("notify.json")
        return render_template("extension/notify_extension.html", notifications=notifications)

    if extension_name == "payment_extension":
        bills = read_json("pay.json")
        return render_template("extension/payment_extension.html", bills=bills)

    return render_template(f"extension/{extension_name}.html")


@app.route("/lienhe")
def lienhe():
    return render_template("lienhe.html")
@app.route("/gioithieu")
def trangchu():
    return render_template("gioithieu.html")


# ================= HOME =================
@app.route("/")
@app.route("/home")
def home_page():
    page = request.args.get("page", 1, type=int)
    apartments, total_pages = dao.load_apartment_paginated(page=page, per_page=5)

    return render_template(
        "home.html",
        apartment=apartments,
        page=page,
        total_pages=total_pages
    )


@app.route('/register', methods=['POST'])
def register_process():
    data = request.form

    if data.get('password') != data.get('confirm'):
        return render_template("register.html", err_msg="Mật khẩu không khớp!")

    try:
        add_user(
            name=data.get('name'),
            username=data.get('username'),
            password=data.get('password'),
            avatar=request.files.get('avatar')
        )
        flash("Đăng ký thành công, vui lòng đăng nhập", "success")
        return redirect(url_for("login_process"))
    except Exception as ex:
        return render_template("register.html", err_msg=str(ex))



@app.route("/login", methods=["GET", "POST"])
def login_process():
    if request.method == "POST":
        username = request.form["username"]
        password = hashlib.md5(request.form["password"].encode()).hexdigest()

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            if user.user_role == UserRole.ADMIN:
                return redirect(url_for("admin.admin_dashboard"))
            return redirect(url_for("home_page"))

        flash("Sai tài khoản hoặc mật khẩu", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout_process():
    logout_user()
    return redirect(url_for("home_page"))

@app.route("/extension/notify_extension")
def notifications_page():
    # Nếu bạn dùng file JSON
    import json, os
    path = os.path.join(app.root_path, "templates", "Data", "notify.json")
    with open(path, "r", encoding="utf-8") as f:
        notifications = json.load(f)

    return render_template("extension/notify_extension.html", notifications=notifications)

@app.route("/extension/payment_extension", methods=["GET"])
def search_invoice():
    invoices = None
    maHoaDon = request.args.get("maHoaDon")
    tenantName = request.args.get("tenantName")

    if maHoaDon or tenantName:
        query = Invoice.query.join(Contract)
        if maHoaDon:
            query = query.filter(Invoice.maHoaDon.ilike(f"%{maHoaDon}%"))
        if tenantName:
            query = query.filter(Contract.tenant_name.ilike(f"%{tenantName}%"))
        invoices = query.all()

    return render_template("extension/payment_extension.html", invoices=invoices)


@app.route("/extension/deal_extension", methods=["GET"])
def search_contract():
    contracts = None
    maHopDong = request.args.get("maHopDong")
    tenantName = request.args.get("tenantName")

    if maHopDong or tenantName:
        query = Contract.query
        if maHopDong:
            query = query.filter(Contract.maHopDong.ilike(f"%{maHopDong}%"))
        if tenantName:
            query = query.filter(Contract.tenant_name.ilike(f"%{tenantName}%"))
        contracts = query.all()

    return render_template("extension/deal_extension.html", contracts=contracts)
@app.route("/extension/contract/<int:contract_id>")
def view_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return render_template("extension/contract_detail.html", contract=contract)

@app.route("/admin-dashboard")
def ad_dashboard():
    return render_template("admin-dashboard.html")

# ================= ADMIN BLUEPRINT =================
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    apartments = dao.get_all_apartments()
    renting = len([a for a in apartments if a.status == "rented"])
    empty = len([a for a in apartments if a.status == "available"])
    return render_template("admin-dashboard.html", renting=renting, empty=empty)


@admin_bp.route("/apartments")
@login_required
def admin_apartments():
    types = dao.get_all_apartment_types()
    return render_template("admin/apartment.html", types=types)


# ================= ADMIN APARTMENT API =================
@admin_bp.route("/api/apartments")
@login_required
def api_get_apartments():
    return jsonify(dao.get_all_apartments_with_type())


@app.route("/admin/api/apartments", methods=["POST"])
@login_required
def api_add_apartment():
    dao.add_apartment(request.form, request.files.get("image"))
    return jsonify({"success": True})


@app.route("/admin/api/apartments/<int:ap_id>", methods=["PUT"])
@login_required
def api_update_apartment(ap_id):
    dao.update_apartment(ap_id, request.form, request.files.get("image"))
    return jsonify({"success": True})


@admin_bp.route("/api/apartments/<int:ap_id>", methods=["DELETE"])
@login_required
def api_delete_apartment(ap_id):
    dao.delete_apartment(ap_id)
    return jsonify(success=True)

            #====ADMIN SERVICES API=====

# ================= SERVICE PAGE =================
@admin_bp.route("/services")
@login_required
def admin_services():
    return render_template("admin/service.html")


# ================= SERVICE API =================
@admin_bp.route("/api/services")
@login_required
def api_get_services():
    return jsonify(dao.get_all_services_json())


@admin_bp.route("/api/services", methods=["POST"])
@login_required
def api_add_service():
    dao.add_service(request.form)
    return jsonify(success=True)


@admin_bp.route("/api/services/<int:sid>", methods=["PUT"])
@login_required
def api_update_service(sid):
    dao.update_service(sid, request.form)
    return jsonify(success=True)


@admin_bp.route("/api/services/<int:sid>", methods=["DELETE"])
@login_required
def api_delete_service(sid):
    dao.delete_service(sid)
    return jsonify(success=True)


            #=======CONTRACTS API=======
@admin_bp.route("/contracts")
@login_required
def admin_contracts():
    apartments = dao.get_all_apartments()
    return render_template("admin/contract.html", apartments=apartments)

@admin_bp.route("/api/contracts")
@login_required
def api_get_contract():
    return jsonify(dao.get_all_contracts())

@admin_bp.route("/api/contracts", methods=["POST"])
@login_required
def api_add_contract():
    try:
        dao.add_contract(request.form)
        return jsonify(success=True)
    except ValueError as e:
        return jsonify(success=False, message=str(e)), 400

@admin_bp.route("/api/contracts/<int:contract_id>", methods=["DELETE"])
@login_required
def api_delete_contract(contract_id):
    try:
        dao.delete_contract(contract_id)
        return jsonify(success=True)
    except ValueError as e:
        return jsonify(success=False, message=str(e)), 400



# ================= REGULATION PAGE =================
@admin_bp.route("/regulations")
@login_required
def admin_regulations():
    return render_template("admin/regulation.html")


# ================= REGULATION API =================
@admin_bp.route("/api/regulations")
@login_required
def api_get_regulations():
    regs = dao.get_all_regulations()
    return jsonify([{
        "maQuyDinh": r.maQuyDinh,
        "tenQuyDinh": r.tenQuyDinh,
        "giaDien": r.giaDien,
        "giaNuoc": r.giaNuoc,
        "phiDichVu": r.phiDichVu,
        "soNguoiToiDa": r.soNguoiToiDa,
        "phiTreHan": r.phiTreHan,
        "ngayBatDau": r.ngayBatDau.strftime("%Y-%m-%d"),
        "ngayKetThuc": r.ngayKetThuc.strftime("%Y-%m-%d") if r.ngayKetThuc else "",
        "ghiChu": r.ghiChu
    } for r in regs])


@admin_bp.route("/api/regulations", methods=["POST"])
@login_required
def api_add_regulation():
    dao.add_regulation(request.form)
    return jsonify(success=True)


@admin_bp.route("/api/regulations/<int:rid>", methods=["PUT"])
@login_required
def api_update_regulation(rid):
    dao.update_regulation(rid, request.form)
    return jsonify(success=True)


@admin_bp.route("/api/regulations/<int:rid>", methods=["DELETE"])
@login_required
def api_delete_regulation(rid):
    dao.delete_regulation(rid)
    return jsonify(success=True)


# ================= INVOICE API =================

# ================= INVOICE ADMIN =================

@admin_bp.route("/invoices")
@login_required
def admin_invoices():
    return render_template("admin/invoice.html")


@admin_bp.route("/invoices/<int:id>")
@login_required
def admin_invoice_detail(id):
    return render_template("admin/invoice_detail_modal.html")


@admin_bp.route("/api/invoices")
@login_required
def api_get_invoices():
    return jsonify(dao.get_all_invoices())


@admin_bp.route("/api/invoices/<int:id>")
@login_required
def api_invoice_detail(id):
    return jsonify(dao.get_invoice_detail(id))


@admin_bp.route("/api/invoices/generate", methods=["POST"])
@login_required
def api_generate_invoices():
    data = request.json
    dao.generate_monthly_invoices(
        int(data["thang"]),
        int(data["nam"])
    )
    return jsonify(success=True)


@admin_bp.route("/api/invoices/<int:id>/pay", methods=["POST"])
@login_required
def api_pay_invoice(id):
    dao.mark_invoice_paid(id)
    return jsonify(success=True)


@admin_bp.route("/api/invoices/<int:id>/pdf")
@login_required
def api_invoice_pdf(id):
    path = dao.export_invoice_pdf(id)
    return send_file(path, as_attachment=False)

            #=========ACCOUNTS API======

@admin_bp.route("/accounts")
@login_required
def admin_accounts():
    return render_template("admin/account.html")

@admin_bp.route("/api/accounts")
@login_required
def api_get_accounts():
    return jsonify(dao.get_all_users())

@admin_bp.route("/api/accounts/<int:id>")
@login_required
def api_account_detail(id):
    return jsonify(dao.get_user_detail(id))

@admin_bp.route("/api/accounts", methods=["POST"])
@login_required
def api_create_account():
    dao.create_user(request.json)
    return jsonify(success=True)

@admin_bp.route("/api/accounts/<int:id>", methods=["PUT"])
@login_required
def api_update_account(id):
    dao.update_user(id, request.json)
    return jsonify(success=True)

# @admin_bp.route("/api/accounts/<int:id>/toggle", methods=["POST"])
# @login_required
# def api_toggle_account(id):
#     dao.toggle_user_active(id)
#     return jsonify(success=True)

@admin_bp.route("/api/accounts/<int:id>/reset", methods=["POST"])
@login_required
def api_reset_password(id):
    dao.reset_password(id)
    return jsonify(success=True)

# ================= THỐNG KÊ =================

@admin_bp.route("/reports")
@login_required
def admin_reports():
    return render_template(
        "admin/report.html",
        current_year=datetime.now().year
    )


@admin_bp.route("/api/reports/apartment-status")
@login_required
def api_stat_apartment():
    return jsonify(dao.stat_apartment_status())


@admin_bp.route("/api/reports/revenue")
@login_required
def api_stat_revenue():
    year = int(request.args.get("year", datetime.today().year))
    values = dao.stat_revenue_by_year(year)

    return jsonify({
        "labels": [f"Tháng {i}" for i in range(1, 13)],
        "values": values
    })


# @admin_bp.route("/api/reports/contracts-expiring")
# @login_required
# def api_contract_expiring():
#     days = int(request.args.get("days", 30))
#     return jsonify(dao.stat_contract_expiring(days))


@admin_bp.route("/api/reports/contracts-expiring")
@login_required
def api_contracts_expiring():
    today = datetime.today()
    limit = today + timedelta(days=30)

    result = []

    contracts = Contract.query.filter(
        Contract.trangThai == ContractStatus.ACTIVE
    ).all()

    for c in contracts:
        end_date = c.ngayBatDau + timedelta(days=c.thoiHan * 30)
        if today <= end_date <= limit:
            result.append({
                "maHopDong": c.maHopDong,
                "tenant": c.tenant_name,
                "ngayHetHan": end_date.strftime("%d/%m/%Y"),
                "days_left": (end_date - today).days
            })

    return jsonify(result)

# @admin_bp.route("/api/reports/contracts-expiring")
# @login_required
# def api_contracts_expiring():
#     today = date.today()
#     limit = today + timedelta(days=30)
#
#     contracts = Contract.query.filter(
#         Contract.ngayBatDau <= limit,
#         Contract.trangThai == ContractStatus.ACTIVE
#     ).all()
#
#     return jsonify([
#         {
#             "maHopDong": c.maHopDong,
#             "tenant": c.tenant_name,
#             "ngayBatDau": c.ngayBatDau.strftime("%d/%m/%Y"),
#             "days_left": (limit - c.ngayBatDau.date()).days
#         } for c in contracts
#     ])
#

app.register_blueprint(admin_bp)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)