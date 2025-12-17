import hashlib
import os
from datetime import datetime, timedelta

import cloudinary.uploader
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from Apartment_manage.models import Apartment, ApartmentType, Contract, User
from Apartment_manage import db
from sqlalchemy.exc import IntegrityError

UPLOAD_FOLDER = "Apartment_manage/static/uploads/apartments"

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
        joinedload(Apartment.type)
    ).all()

    return [{
        "id": a.id,
        "title": a.title,
        "price": a.price,
        "area": a.area,
        "status": a.status,
        "type_id": a.type_id,
        "type_name": a.type.tenLoai if a.type else "",
        "image_url": a.image_url,
        "description_short": a.description_short
    } for a in apartments]

def save_image(file):
    if not file:
        return None

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    return f"/static/uploads/apartments/{filename}"

def add_apartment(data, image_file):
    image_url = save_image(image_file) if image_file else None

    ap = Apartment(
        title=data["title"],
        price=float(data["price"]),
        area=float(data["area"]),
        type_id=int(data["type_id"]),
        description_short=data.get("description_short", ""),
        image_url=image_url,
        status="available"
    )

    db.session.add(ap)
    db.session.commit()



def update_apartment(ap_id, data, image_file):
    ap = Apartment.query.get_or_404(ap_id)

    ap.title = data["title"]
    ap.price = float(data["price"])
    ap.area = float(data["area"])
    ap.type_id = int(data["type_id"])
    ap.description_short = data.get("description_short", "")

    if image_file:
        ap.image_url = save_image(image_file)

    db.session.commit()


def delete_apartment(ap_id):
    ap = Apartment.query.get(ap_id)
    if ap:
        db.session.delete(ap)
        db.session.commit()


# Contracts expiring (helper)
def get_expiring_contracts(days=30):
    limit = datetime.today() + timedelta(days=days)
    return Contract.query.filter(Contract.ngayBatDau <= limit).all()