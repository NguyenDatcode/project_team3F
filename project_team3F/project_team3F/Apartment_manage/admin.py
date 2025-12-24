from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user

from Apartment_manage import dao, db
from Apartment_manage.dao import get_all_apartments
from flask import Blueprint, render_template, request, jsonify, redirect

from Apartment_manage.models import UserRole, app, ApartmentType, Apartment
from database import get_all_apartments, get_all_apartment_types


class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class ApartmentView(AdminView):
    column_list = ['id', 'title', 'price', 'area', 'type_id', 'status']
    column_searchable_list = ['title']
    column_filters = ['price', 'status', 'type_id']
    form_columns = ['title', 'price', 'area', 'bedrooms', 'bathrooms',
                    'floor', 'status', 'location', 'is_vip', 'image_url',
                    'description_short', 'type_id']
    page_size = 30


class ApartmentTypeView(AdminView):
    column_list = ['id', 'tenLoai', 'giaCoBan', 'dienTich']
    form_columns = ['tenLoai', 'giaCoBan', 'dienTich', 'moTa']


class LogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('admin/index.html')


admin = Admin(app, name="Apartment Admin", index_view=MyAdminIndexView())

# Add SQLA Views
admin.add_view(ApartmentTypeView(ApartmentType, db.session, name="Loại căn hộ"))
admin.add_view(ApartmentView(Apartment, db.session, name="Căn hộ"))
admin.add_view(LogoutView(name="Đăng xuất"))