import hashlib
import cloudinary.uploader
from sqlalchemy.orm import joinedload

from Apartment_manage.models import Apartment, ApartmentType, Contract, User
from Apartment_manage import db
from sqlalchemy.exc import IntegrityError

def load_apartment_paginated(page=1, per_page=5):
    paginate_obj = Apartment.query.paginate(page=page, per_page=per_page, error_out=False)
    return paginate_obj.items, paginate_obj.pages

# ========= USER =========
def add_user(name, username, password, avatar):
    password = hashlib.md5(password.encode()).hexdigest()
    u = User(name=name, username=username, password=password)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res["secure_url"]

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Username đã tồn tại")


def get_user_by_id(uid):
    return User.query.get(int(uid))


# ========= APARTMENT =========
def get_all_apartment_types():
    return ApartmentType.query.all()


def get_all_apartments():
    return Apartment.query.all()


def get_all_apartments_with_type():
    apartments = Apartment.query.options(
        joinedload(Apartment.apartment_type)
    ).all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "price": a.price,
            "status": a.status,
            "type_id": a.type_id,
            "type_name": a.apartment_type.tenLoai if a.apartment_type else ""
        }
        for a in apartments
    ]


def add_apartment(data):
    ap = Apartment(
        title=data["title"],
        price=data["price"],
        status=data["status"],
        type_id=data["apartment_type_id"]
    )
    db.session.add(ap)
    db.session.commit()


def update_apartment(ap_id, data):
    ap = Apartment.query.get(ap_id)
    if not ap:
        return
    ap.title = data["title"]
    ap.price = data["price"]
    ap.status = data["status"]
    ap.type_id = data["apartment_type_id"]
    db.session.commit()


def delete_apartment(ap_id):
    ap = Apartment.query.get(ap_id)
    if ap:
        db.session.delete(ap)
        db.session.commit()