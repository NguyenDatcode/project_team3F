import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as UserEnum
from flask_login import UserMixin

from Apartment_manage import db, create_app

app = create_app()

# =====================================================
# BASE MODEL
# =====================================================
class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)


# =====================================================
# USER + ROLE
# =====================================================
class UserRole(UserEnum):
    USER = 1
    ADMIN = 2


# class User(BaseModel, UserMixin):
#     name = Column(String(50), nullable=False)
#     avatar = Column(String(255),
#                     default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
#
#     username = Column(String(50), unique=True, nullable=False)
#     password = Column(String(255), nullable=False)
#
#     user_role = Column(db.Enum(UserRole), default=UserRole.USER)
#
#     def __str__(self):
#         return self.name


class User(BaseModel, UserMixin):
    __tablename__ = "user"

    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(255))
    user_role = db.Column(db.Enum(UserRole), default=UserRole.USER)

    def __str__(self):
        return f"<User {self.username}>"


# ============================
# APARTMENT TYPE
# ============================
# models.py
# ============================
# APARTMENT TYPE
# ============================
class ApartmentType(BaseModel):
    __tablename__ = "apartment_type"

    tenLoai = db.Column(db.String(100), nullable=False)
    giaCoBan = db.Column(db.Float, default=0.0)
    dienTich = db.Column(db.Float, default=0.0)
    moTa = db.Column(db.Text)

    apartments = db.relationship("Apartment", backref="type", lazy=True)

    def __str__(self):
        return self.tenLoai


# ============================
# APARTMENT
# ============================
class Apartment(BaseModel):
    __tablename__ = "apartment"

    title = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, default=0)
    area = db.Column(db.Float, default=0)
    bedrooms = db.Column(db.Integer, default=0)
    bathrooms = db.Column(db.Integer, default=0)
    floor = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default="available")
    location = db.Column(db.String(100))
    is_vip = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255))
    description_short = db.Column(db.String(255))

    type_id = db.Column(db.Integer, db.ForeignKey("apartment_type.id"))

    def __str__(self):
        return self.title


# ============================
# CONTRACT (OPTIONAL)
# ============================
class Contract(BaseModel):
    __tablename__ = "contract"

    tenant_name = db.Column(db.String(100))
    ngayBatDau = db.Column(db.DateTime, default=datetime.utcnow)
    apartment_id = db.Column(db.Integer, db.ForeignKey("apartment.id"))

    apartment = db.relationship("Apartment", backref=db.backref("contracts", lazy=True))
# =====================================================
# SERVICE – DỊCH VỤ
# =====================================================
class Service(BaseModel):
    maDichVu = Column(String(50), unique=True, nullable=False)
    tenDichVu = Column(String(255), nullable=False)
    donGia = Column(Float, nullable=False)
    donViTinh = Column(String(50))
    loaiTinhPhi = Column(String(100))

    invoice_details = relationship("InvoiceDetail", backref="service", lazy=True)

    def __str__(self):
        return self.tenDichVu


# =====================================================
# INVOICE – HÓA ĐƠN
# =====================================================
class Invoice(BaseModel):
    maHoaDon = Column(String(50), unique=True, nullable=False)
    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    tongTien = Column(Float, default=0)

    apartment_id = Column(Integer, ForeignKey(Apartment.id), nullable=False)

    invoice_details = relationship("InvoiceDetail", backref="invoice", lazy=True)

    def __str__(self):
        return self.maHoaDon


# =====================================================
# INVOICE DETAIL – CHI TIẾT HÓA ĐƠN
# =====================================================
class InvoiceDetail(BaseModel):
    maCTHD = Column(String(50), unique=True, nullable=False)

    maHoaDon_id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
    maDichVu_id = Column(Integer, ForeignKey(Service.id), nullable=False)

    moTa = Column(Text)
    chiSoCu = Column(Float)
    chiSoMoi = Column(Float)

    donGiaApDung = Column(Float, nullable=False)
    soLuong = Column(Float, nullable=False)
    thanhTien = Column(Float, nullable=False)

    def __str__(self):
        return self.maCTHD

def load_sample_data():
    with open("Apartment_manage/json/apartment.json", "r", encoding="utf-8") as f:
        apartments = json.load(f)

    with open("Apartment_manage/json/apartment_type.json", "r", encoding="utf-8") as f:
        types = json.load(f)

    # tránh add trùng nếu DB đã có
    if ApartmentType.query.count() == 0:
        for t in types:
            db.session.add(ApartmentType(**t))

    if Apartment.query.count() == 0:
        for a in apartments:
            db.session.add(Apartment(**a))

    db.session.commit()

# =====================================================
# CREATE TABLE + IMPORT JSON
# =====================================================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        import hashlib

        # --- USER ---
        if User.query.count() == 0:
            u = User(
                name="admin",
                username="admin",
                password=str(hashlib.md5("123456".encode()).hexdigest()),
                user_role=UserRole.ADMIN
            )
            db.session.add(u)
            db.session.commit()

        # --- APARTMENT TYPE ---
        try:
            with open("templates/Data/apartment_type.json", encoding="utf-8") as f:
                types = json.load(f)

                if ApartmentType.query.count() == 0:
                    for t in types:
                        db.session.add(ApartmentType(**t))
            db.session.commit()
        except Exception as e:
            print("Error loading apartment_type.json:", e)

        # --- APARTMENT ---
        try:
            with open("templates/Data/apartment.json", encoding="utf-8") as f:
                apartments = json.load(f)

                if Apartment.query.count() == 0:
                    for a in apartments:
                        db.session.add(Apartment(**a))
            db.session.commit()
        except Exception as e:
            print("Error loading apartment.json:", e)

        print("Database initialized successfully!")
