import hashlib
import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_user, login_required

from Apartment_manage import dao, login, create_app, db
from Apartment_manage.dao import add_user
from Apartment_manage.models import User, UserRole, Invoice, Apartment, Contract

app = create_app()


# ============================
# LOGIN MANAGER
# ============================
@login.user_loader
def load_user(uid):
    return dao.get_user_by_id(uid)


# ============================
# HOME
# ============================
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





# ============================
# LOGIN / LOGOUT
# ============================
@app.route('/login', methods=['GET', 'POST'])
def login_process():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            flash("Đăng nhập thành công", "success")
            if user.user_role == UserRole.USER:
                return redirect(url_for("home_page"))
            elif user.user_role == UserRole.ADMIN:
                return redirect(url_for("admin_dashboard"))

        flash("Tài khoản không tồn tại hoặc chưa đăng ký!", "danger")
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout_process():
    logout_user()
    flash("Đã đăng xuất thành công", "info")
    return redirect(url_for('home_page'))


# ============================
# REGISTER
# ============================
@app.route('/register', methods=['GET'])
def load_register():
    return render_template('register.html')


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


# ============================
# ADMIN DASHBOARD
# ============================
@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    apartments = dao.get_all_apartments()
    renting = len([a for a in apartments if a.status == "rented"])
    empty = len([a for a in apartments if a.status == "available"])
    return render_template("admin-dashboard.html", renting=renting, empty=empty)


# ============================
# API LOAD CONTENT
# ============================
@app.route("/api/admin/apartment_content")
@login_required
def apartment_content_api():
    types = dao.load_apartment_types()
    return render_template("admin/apartment.html", types=types)


@app.route("/api/admin/apartment_type_content")
@login_required
def apartment_type_content_api():
    return render_template("admin/apartment_type.html")

# ============================
# READ JSON
# ============================
def read_json(filename):
    path = os.path.join(app.root_path, "templates", "Data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/index")
def index():
    notifications = read_json("notify.json")
    bills = read_json("pay.json")
    return render_template("index.html", notifications=notifications, bills=bills)
@app.route("/rule")
def load_rule():
    return render_template("rule.html")

@app.route("/extension/notify_extension")
def notifications_page():
    # Nếu bạn dùng file JSON
    import json, os
    path = os.path.join(app.root_path, "templates", "Data", "notify.json")
    with open(path, "r", encoding="utf-8") as f:
        notifications = json.load(f)

    return render_template("extension/notify_extension.html", notifications=notifications)
# ============================
# EXTENSIONS
# ============================
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

# ============================
# API APARTMENTS
# ============================
@app.route("/api/apartments")
def api_apartments():
    data = dao.get_all_apartments_with_type()
    return jsonify(data)


@app.route("/apartment")
def apartment_page():
    apartments = dao.get_all_apartments_with_type()
    types = dao.get_apartment_types()
    return render_template("apartment.html", apartments=apartments, types=types)


@app.route("/lienhe")
def lienhe():
    return render_template("lienhe.html")


@app.route("/gioithieu")
def trangchu():
    return render_template("gioithieu.html")


# ============================
# RUN APP
# ============================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
