# Apartment_manage/dao.py
import hashlib
from datetime import datetime, timedelta

import cloudinary.uploader
from sqlalchemy.orm import joinedload

from Apartment_manage.models import Apartment, ApartmentType, Contract, User
from Apartment_manage import db
from sqlalchemy.exc import IntegrityError

def get_apartment_types():
    """Trả về list các ApartmentType (SQLAlchemy objects)"""
    try:
        return ApartmentType.query.filter(ApartmentType.active == True).order_by(ApartmentType.id.asc()).all()
    except Exception as e:
        print("Lỗi get_apartment_types:", e)
        return []

def get_all_apartments_with_type():
    """
    Trả về list of dict: mỗi phần tử chứa thông tin căn hộ + tên loại.
    Dùng SQLAlchemy, an toàn và portable.
    """
    try:
        # load relationship apartment_type để tránh N+1
        apartments = Apartment.query.options(joinedload(Apartment.apartment_type)).order_by(Apartment.id.desc()).all()
        result = []
        for a in apartments:
            result.append({
                "id": a.id,
                "title": a.title,
                "price": a.price,
                "area": a.area,
                "bedrooms": a.bedrooms,
                "bathrooms": a.bathrooms,
                "floor": a.floor,
                "status": a.status,
                "location": a.location,
                "is_vip": bool(a.is_vip),
                "type_id": getattr(a, 'type_id', None) or getattr(a, 'apartment_type_id', None),
                # tên loại tùy thuộc tên property relationship bạn đặt: a.apartment_type hoặc a.type
                "type_name": (a.apartment_type.name if hasattr(a, 'apartment_type') and a.apartment_type else
                              (a.type.name if hasattr(a, 'type') and a.type else None))
            })
        return result
    except Exception as ex:
        print("Lỗi get_all_apartments_with_type:", ex)
        return []

def get_apartment_type_by_id(type_id):
    return ApartmentType.query.get(type_id)

def create_apartment_type(name, base_price=0.0, area_default=0.0, description=None):
    at = ApartmentType(name=name, base_price=base_price, area_default=area_default, description=description)
    db.session.add(at)
    db.session.commit()
    return at

def update_apartment_type(type_id, **kwargs):
    at = ApartmentType.query.get(type_id)
    if not at:
        return None
    for k,v in kwargs.items():
        if hasattr(at, k):
            setattr(at, k, v)
    db.session.commit()
    return at

def delete_apartment_type(type_id):
    at = ApartmentType.query.get(type_id)
    if not at: return False
    db.session.delete(at)
    db.session.commit()
    return True

# Apartments
def get_all_apartments():
    return Apartment.query.order_by(Apartment.id).all()

def get_apartment_by_id(ap_id):
    return Apartment.query.get(ap_id)

def create_apartment(**data):
    a = Apartment(**data)
    db.session.add(a)
    db.session.commit()
    return a

def update_apartment(apartment_id, **kwargs):
    a = Apartment.query.get(apartment_id)
    if not a: return None
    for k,v in kwargs.items():
        if hasattr(a, k):
            setattr(a, k, v)
    db.session.commit()
    return a

def delete_apartment(apartment_id):
    a = Apartment.query.get(apartment_id)
    if not a: return False
    db.session.delete(a)
    db.session.commit()
    return True

# Contracts expiring (helper)
def get_expiring_contracts(days=30):
    limit = datetime.today() + timedelta(days=days)
    return Contract.query.filter(Contract.ngayBatDau <= limit).all()

# Users / auth helpers
def get_user_by_id(uid):
    return User.query.get(int(uid))

def auth_user(username, password_plain):
    hashed = hashlib.md5(password_plain.encode('utf-8')).hexdigest()
    return User.query.filter(User.username == username, User.password == hashed).first()

# ============================
# PAGINATION: APARTMENT LIST
# ============================
def load_apartment_paginated(page=1, per_page=5):
    paginate_obj = Apartment.query.paginate(page=page, per_page=per_page, error_out=False)
    return paginate_obj.items, paginate_obj.pages

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


def load_apartment_types():
    """
    Tải danh sách tất cả các loại căn hộ đang hoạt động (active=True) từ cơ sở dữ liệu.
    """
    try:
        # Truy vấn tất cả các loại căn hộ và sắp xếp theo ID
        types = ApartmentType.query.filter(ApartmentType.active.__eq__(True)).order_by(ApartmentType.id.asc()).all()

        # Nếu cần chuyển sang định dạng Dictionary (nếu view cần dữ liệu đơn giản hơn)
        # Tuy nhiên, trong trường hợp này, việc trả về đối tượng SQLAlchemy là tốt nhất
        return types

    except Exception as ex:
        # In lỗi ra console để debug
        print(f"LỖI TẢI LOẠI CĂN HỘ: {ex}")
        return []  # Trả về danh sách rỗng nếu có lỗi xảy ra