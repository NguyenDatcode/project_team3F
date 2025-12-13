# # Apartment_manage/dao.py
# import hashlib
# from datetime import datetime, timedelta
#
# import cloudinary.uploader
# from .models import Apartment, ApartmentType, Contract, User
# from . import db
# from sqlalchemy.exc import IntegrityError
#
# def get_apartment_types():
#     return ApartmentType.query.all()
#
# # Lấy tất cả căn hộ
# def get_all_apartments():
#     return Apartment.query.join(ApartmentType).add_columns(
#         Apartment.id,
#         Apartment.title,
#         Apartment.price,
#         Apartment.status,
#         ApartmentType.tenLoai
#     ).all()
#
# def get_all_apartments_with_type():
#     return db.session.query(Apartment, ApartmentType).join(
#         ApartmentType,
#         Apartment.type_id == ApartmentType.id
#     ).all()
#
# # Lấy một căn hộ
# def get_apartment_by_id(apartment_id):
#     return Apartment.query.get(apartment_id)
#
# # Thêm mới
# def add_apartment(data):
#     a = Apartment(**data)
#     db.session.add(a)
#     db.session.commit()
#     return a
#
# # Cập nhật
# def update_apartment(apartment_id, data):
#     a = Apartment.query.get(apartment_id)
#     if not a:
#         return None
#     for key, value in data.items():
#         setattr(a, key, value)
#     db.session.commit()
#     return a
#
# def create_apartment_type(name, base_price=0.0, area_default=0.0, description=None):
#     at = ApartmentType(name=name, base_price=base_price, area_default=area_default, description=description)
#     db.session.add(at)
#     db.session.commit()
#     return at
#
# def update_apartment_type(type_id, **kwargs):
#     at = ApartmentType.query.get(type_id)
#     if not at:
#         return None
#     for k,v in kwargs.items():
#         if hasattr(at, k):
#             setattr(at, k, v)
#     db.session.commit()
#     return at
#
# def delete_apartment_type(type_id):
#     at = ApartmentType.query.get(type_id)
#     if not at: return False
#     db.session.delete(at)
#     db.session.commit()
#     return True
#
#
# def create_apartment(**data):
#     a = Apartment(**data)
#     db.session.add(a)
#     db.session.commit()
#     return a
#
#
# # Xóa
# def delete_apartment(apartment_id):
#     a = Apartment.query.get(apartment_id)
#     if not a:
#         return False
#     db.session.delete(a)
#     db.session.commit()
#     return True
#
# # Contracts expiring (helper)
# def get_expiring_contracts(days=30):
#     limit = datetime.today() + timedelta(days=days)
#     return Contract.query.filter(Contract.ngayBatDau <= limit).all()
#
# # Users / auth helpers
# def get_user_by_id(uid):
#     return User.query.get(int(uid))
#
# def auth_user(username, password_plain):
#     hashed = hashlib.md5(password_plain.encode('utf-8')).hexdigest()
#     return User.query.filter(User.username == username, User.password == hashed).first()
#
# # ============================
# # PAGINATION: APARTMENT LIST
# # ============================
# def load_apartment_paginated(page=1, per_page=5):
#     paginate_obj = Apartment.query.paginate(page=page, per_page=per_page, error_out=False)
#     return paginate_obj.items, paginate_obj.pages
#
#
#
# def load_apartment_types():
#     """
#     Tải danh sách tất cả các loại căn hộ đang hoạt động (active=True) từ cơ sở dữ liệu.
#     """
#     try:
#         # Truy vấn tất cả các loại căn hộ và sắp xếp theo ID
#         types = ApartmentType.query.filter(ApartmentType.active.__eq__(True)).order_by(ApartmentType.id.asc()).all()
#
#         # Nếu cần chuyển sang định dạng Dictionary (nếu view cần dữ liệu đơn giản hơn)
#         # Tuy nhiên, trong trường hợp này, việc trả về đối tượng SQLAlchemy là tốt nhất
#         return types
#
#     except Exception as ex:
#         # In lỗi ra console để debug
#         print(f"LỖI TẢI LOẠI CĂN HỘ: {ex}")
#         return []  # Trả về danh sách rỗng nếu có lỗi xảy ra
#
import hashlib

from cloudinary.templatetags import cloudinary
from pymysql import IntegrityError

# Apartment_manage/dao.py

from .models import Apartment, ApartmentType, User
from . import db

# ---------------------------
# LOAD TYPES
# ---------------------------
def get_apartment_types():
    return ApartmentType.query.all()


# ---------------------------
# LOAD ALL APARTMENTS + TYPE
# (TRẢ VỀ LIST OBJECT Apartment)
# ---------------------------
def get_all_apartments():
    return Apartment.query.options(
        db.joinedload(Apartment.apartment_type)
    ).all()



# ---------------------------
# LOAD APARTMENTS AS DICTIONARY
# (DÙNG API JSON)
# ---------------------------
def get_all_apartments_with_type():
    data = []
    apartments = Apartment.query.options(
        db.joinedload(Apartment.apartment_type)
    ).all()

    for a in apartments:
        data.append({
            "id": a.id,
            "title": a.title,
            "price": a.price,
            "area": a.area,
            "bedrooms": a.bedrooms,
            "bathrooms": a.bathrooms,
            "floor": a.floor,
            "status": a.status,
            "type_name": a.apartment_type.tenLoai if a.apartment_type else None
        })
    return data



# ---------------------------
# CRUD
# ---------------------------

def get_apartment_by_id(apartment_id):
    return Apartment.query.get(apartment_id)

# Users / auth helpers
def get_user_by_id(uid):
    return User.query.get(int(uid))

def add_apartment(data):
    a = Apartment(**data)
    db.session.add(a)
    db.session.commit()
    return a


def update_apartment(apartment_id, data):
    a = Apartment.query.get(apartment_id)
    if not a:
        return None

    for key, value in data.items():
        setattr(a, key, value)

    db.session.commit()
    return a


def delete_apartment(apartment_id):
    a = Apartment.query.get(apartment_id)
    if not a:
        return False

    db.session.delete(a)
    db.session.commit()
    return True


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name.strip(), username=username.strip(), password=password)
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception('Tên đăng nhập đã tồn tại!')
