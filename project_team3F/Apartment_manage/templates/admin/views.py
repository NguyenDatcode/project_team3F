# from flask import render_template
# from flask_login import login_required
#
# from Apartment_manage import dao
# from Apartment_manage.app import app
#
#
# # ============================
# # ADMIN DASHBOARD
# # ============================
# @app.route('/admin-dashboard')
# @login_required
# def load_admin_dashboard():
#
#     apartments = dao.load_apartments()
#     renting = len([a for a in apartments if a["status"] == "rented"])
#     empty = len([a for a in apartments if a["status"] == "available"])
#
#     months = ["1", "2", "3", "4", "5", "6"]
#     revenue = [5, 7, 3, 8, 10, 4]
#
#     expiring = dao.get_expiring_contracts()
#
#     return render_template(
#         "admin/admin-dashboard.html",
#         renting=renting,
#         empty=empty,
#         months=months,
#         revenue=revenue,
#         expiring=expiring
#     )