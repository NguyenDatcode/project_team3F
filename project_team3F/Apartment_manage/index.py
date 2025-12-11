import hashlib
import json
import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import logout_user, login_user, login_required

from Apartment_manage import dao, login, create_app, db
from Apartment_manage.dao import add_user
from Apartment_manage.models import User, UserRole
# from Apartment_manage.admin import admin_bp


app = create_app()

# app.register_blueprint(admin_bp)

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
# LOGIN
# ============================
@app.route('/login', methods=['GET', 'POST'])
def login_process():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)

            # USER LOGIN
            if user.user_role == UserRole.USER:
                flash("Đã đăng nhập thành công", "success")
                return redirect(url_for("home_page"))

            # ADMIN LOGIN
            if user.user_role == UserRole.ADMIN:
                flash("Đã đăng nhập thành công", "success")
                return redirect(url_for("admin_dashboard"))

        flash("Tài khoản không tồn tại hoặc chưa đăng ký!", "danger")

    return render_template("login.html")


# ============================
# LOGOUT
# ============================
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
# ... (các imports và routes khác giữ nguyên) ...

# ============================
# ADMIN DASHBOARD
# Tuyến đường chính cho giao diện admin (Base page)
# ============================
@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    from Apartment_manage import dao
    apartments = dao.get_all_apartments()
    renting = len([a for a in apartments if a.status == "rented"])
    empty = len([a for a in apartments if a.status == "available"])
    return render_template("admin-dashboard.html", renting=renting, empty=empty)


# ============================
# API: TRẢ VỀ NỘI DUNG ĐỘNG (Dùng để load vào #dynamicContent)
# ============================

# API tải nội dung Căn hộ
# API: Căn hộ
@app.route("/api/admin/apartment_content")
@login_required
def apartment_content_api():
    types = dao.load_apartment_types()
    return render_template("admin/apartment.html", types=types)


# API tải nội dung Loại căn hộ
# API: Loại căn hộ
@app.route("/api/admin/apartment_type_content")
@login_required
def apartment_type_content_api():
    return render_template("admin/apartment_type.html")

# ... (các routes khác giữ nguyên) ...

# ============================
# READ JSON (Extensions)
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


@app.route("/extension/<extension_name>")
def load_extension(extension_name):
    if extension_name == "notify_extension":
        notifications = read_json("notify.json")
        return render_template("extension/notify_extension.html", notifications=notifications)

    if extension_name == "payment_extension":
        bills = read_json("pay.json")
        return render_template("extension/payment_extension.html", bills=bills)

    return render_template(f"extension/{extension_name}.html")

@app.route("/admin/apartment")
@login_required
def admin_apartment():
    types = dao.load_apartment_types()
    return render_template("admin/apartment.html", types=types)


@app.route("/admin/apartment-type")
def apartment_types_page():
    types = dao.load_apartment_types()
    return render_template("admin/apartment_type.html", types=types)


@app.route("/api/apartments")
def api_apartments():
    data = dao.get_all_apartments_with_type()  # list of dict
    return jsonify(data)

@app.route("/apartment")
def apartment_page():
    apartments = dao.get_all_apartments_with_type()
    types = dao.get_apartment_types()
    return render_template("apartment.html", apartments=apartments, types=types)


# ============================
# RUN APP
# ============================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)