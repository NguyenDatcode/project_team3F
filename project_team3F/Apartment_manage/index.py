import hashlib
import json
import os
from flask import render_template, request, redirect, url_for, flash, jsonify, Blueprint
from flask_login import logout_user, login_user, login_required

from Apartment_manage import dao, login, create_app, db
from Apartment_manage.dao import add_user
from Apartment_manage.models import User, UserRole, Contract, Invoice

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
@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin-dashboard.html")

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


# ================= ADMIN API =================
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


app.register_blueprint(admin_bp)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)