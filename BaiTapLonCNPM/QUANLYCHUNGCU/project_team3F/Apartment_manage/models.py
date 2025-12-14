# import json
# from datetime import datetime
# from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
# from enum import Enum as UserEnum
# from flask_login import UserMixin
#
# from Apartment_manage import db, create_app
#
# app = create_app()
#
# # =====================================================
# # BASE MODEL
# # =====================================================
# class BaseModel(db.Model):
#     __abstract__ = True
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     active = Column(Boolean, default=True)
#
#
# # =====================================================
# # USER + ROLE
# # =====================================================
# class UserRole(UserEnum):
#     USER = 1
#     ADMIN = 2
#
#
# # class User(BaseModel, UserMixin):
# #     name = Column(String(50), nullable=False)
# #     avatar = Column(String(255),
# #                     default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
# #
# #     username = Column(String(50), unique=True, nullable=False)
# #     password = Column(String(255), nullable=False)
# #
# #     user_role = Column(db.Enum(UserRole), default=UserRole.USER)
# #
# #     def __str__(self):
# #         return self.name
#
#
# class User(BaseModel, UserMixin):
#     __tablename__ = "user"
#
#     name = db.Column(db.String(50), nullable=False)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     avatar = db.Column(db.String(255))
#     user_role = db.Column(db.Enum(UserRole), default=UserRole.USER)
#
#     def __str__(self):
#         return f"<User {self.username}>"
#
#
# # ============================
# # APARTMENT TYPE
# # ============================
# # models.py
# # ============================
# # APARTMENT TYPE
# # ============================
# class ApartmentType(BaseModel):
#     __tablename__ = "apartment_type"
#
#     tenLoai = db.Column(db.String(100), nullable=False)
#     giaCoBan = db.Column(db.Float, default=0.0)
#     dienTich = db.Column(db.Float, default=0.0)
#     moTa = db.Column(db.Text)
#
#     apartments = db.relationship("Apartment", backref="apartment_type", lazy=True)
#
#     def __str__(self):
#         return self.tenLoai
#
#
# # ============================
# # APARTMENT
# # ============================
# class Apartment(BaseModel):
#     __tablename__ = "apartment"
#
#     title = db.Column(db.String(150), nullable=False)
#     price = db.Column(db.Float, default=0)
#     area = db.Column(db.Float, default=0)
#     bedrooms = db.Column(db.Integer, default=0)
#     bathrooms = db.Column(db.Integer, default=0)
#     floor = db.Column(db.Integer, default=1)
#     status = db.Column(db.String(20), default="available")
#     location = db.Column(db.String(100))
#     is_vip = db.Column(db.Boolean, default=False)
#     image_url = db.Column(db.String(255))
#     description_short = db.Column(db.String(255))
#
#     type_id = db.Column(db.Integer, db.ForeignKey("apartment_type.id"))
#
#     def __str__(self):
#         return self.title
#
#
# # ============================
# # CONTRACT (OPTIONAL)
# # ============================
# class Contract(BaseModel):
#     __tablename__ = "contract"
#
#     tenant_name = db.Column(db.String(100))
#     ngayBatDau = db.Column(db.DateTime, default=datetime.utcnow)
#     apartment_id = db.Column(db.Integer, db.ForeignKey("apartment.id"))
#
#     apartment = db.relationship("Apartment", backref=db.backref("contracts", lazy=True))
# # =====================================================
# # SERVICE – DỊCH VỤ
# # =====================================================
# class Service(BaseModel):
#     maDichVu = Column(String(50), unique=True, nullable=False)
#     tenDichVu = Column(String(255), nullable=False)
#     donGia = Column(Float, nullable=False)
#     donViTinh = Column(String(50))
#     loaiTinhPhi = Column(String(100))
#
#     invoice_details = relationship("InvoiceDetail", backref="service", lazy=True)
#
#     def __str__(self):
#         return self.tenDichVu
#
#
# # =====================================================
# # INVOICE – HÓA ĐƠN
# # =====================================================
# class Invoice(BaseModel):
#     maHoaDon = Column(String(50), unique=True, nullable=False)
#     thang = Column(Integer, nullable=False)
#     nam = Column(Integer, nullable=False)
#     tongTien = Column(Float, default=0)
#
#     apartment_id = Column(Integer, ForeignKey(Apartment.id), nullable=False)
#
#     invoice_details = relationship("InvoiceDetail", backref="invoice", lazy=True)
#
#     def __str__(self):
#         return self.maHoaDon
#
#
# # =====================================================
# # INVOICE DETAIL – CHI TIẾT HÓA ĐƠN
# # =====================================================
# class InvoiceDetail(BaseModel):
#     maCTHD = Column(String(50), unique=True, nullable=False)
#
#     maHoaDon_id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
#     maDichVu_id = Column(Integer, ForeignKey(Service.id), nullable=False)
#
#     moTa = Column(Text)
#     chiSoCu = Column(Float)
#     chiSoMoi = Column(Float)
#
#     donGiaApDung = Column(Float, nullable=False)
#     soLuong = Column(Float, nullable=False)
#     thanhTien = Column(Float, nullable=False)
#
#     def __str__(self):
#         return self.maCTHD
#
# def load_sample_data():
#     with open("Apartment_manage/json/apartment.json", "r", encoding="utf-8") as f:
#         apartments = json.load(f)
#
#     with open("Apartment_manage/json/apartment_type.json", "r", encoding="utf-8") as f:
#         types = json.load(f)
#
#     # tránh add trùng nếu DB đã có
#     if ApartmentType.query.count() == 0:
#         for t in types:
#             db.session.add(ApartmentType(**t))
#
#     if Apartment.query.count() == 0:
#         for a in apartments:
#             db.session.add(Apartment(**a))
#
#     db.session.commit()
#
# # =====================================================
# # CREATE TABLE + IMPORT JSON
# # =====================================================
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#
#         import hashlib
#
#         # --- USER ---
#         if User.query.count() == 0:
#             u = User(
#                 name="admin",
#                 username="admin",
#                 password=str(hashlib.md5("123456".encode()).hexdigest()),
#                 user_role=UserRole.ADMIN
#             )
#             db.session.add(u)
#             db.session.commit()
#
#         # --- APARTMENT TYPE ---
#         try:
#             with open("templates/Data/apartment_type.json", encoding="utf-8") as f:
#                 types = json.load(f)
#
#                 if ApartmentType.query.count() == 0:
#                     for t in types:
#                         db.session.add(ApartmentType(**t))
#             db.session.commit()
#         except Exception as e:
#             print("Error loading apartment_type.json:", e)
#
#         # --- APARTMENT ---
#         try:
#             with open("templates/Data/apartment.json", encoding="utf-8") as f:
#                 apartments = json.load(f)
#
#                 if Apartment.query.count() == 0:
#                     for a in apartments:
#                         db.session.add(Apartment(**a))
#             db.session.commit()
#         except Exception as e:
#             print("Error loading apartment.json:", e)
#
#         print("Database initialized successfully!")

import json
import hashlib
from datetime import datetime
from enum import Enum as PyEnum

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Enum as SQLEnum
from Apartment_manage import db, create_app

app = create_app()

# =====================================================
# ENUMS
# =====================================================
class UserRole(PyEnum):
    USER = 1
    ADMIN = 2

class ContractStatus(PyEnum):
    ACTIVE = "Còn hiệu lực"
    INACTIVE = "Hết hiệu lực"
    TERMINATED = "Chấm dứt"

class InvoiceStatus(PyEnum):
    PAID = "Đã thanh toán"
    UNPAID = "Chưa thanh toán"

# =====================================================
# BASE MODEL
# =====================================================
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)

# =====================================================
# USER MODEL
# =====================================================
class User(BaseModel, UserMixin):
    __tablename__ = "user"

    name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    avatar = Column(String(255))
    user_role = Column(SQLEnum(UserRole), default=UserRole.USER)

    def __str__(self):
        return f"<User {self.username}>"

# =====================================================
# APARTMENT TYPE
# =====================================================
class ApartmentType(BaseModel):
    __tablename__ = "apartment_type"

    tenLoai = Column(String(100), nullable=False)
    giaCoBan = Column(Float, default=0.0)
    dienTich = Column(Float, default=0.0)
    moTa = Column(Text)

    apartments = relationship("Apartment", backref="type", lazy=True)

    def __str__(self):
        return self.tenLoai

# =====================================================
# APARTMENT
# =====================================================
class Apartment(BaseModel):
    __tablename__ = "apartment"

    title = Column(String(150), nullable=False)
    price = Column(Float, default=0)
    area = Column(Float, default=0)
    bedrooms = Column(Integer, default=0)
    bathrooms = Column(Integer, default=0)
    floor = Column(Integer, default=1)
    status = Column(String(20), default="available")
    location = Column(String(100))
    is_vip = Column(Boolean, default=False)
    image_url = Column(String(255))
    description_short = Column(String(255))

    type_id = Column(Integer, ForeignKey("apartment_type.id"))

    def __str__(self):
        return self.title

# =====================================================
# CONTRACT
# =====================================================
class Contract(BaseModel):
    __tablename__ = "contract"

    maHopDong = Column(String(100), nullable=False, unique=True)
    tenant_name = Column(String(100), nullable=False)
    thoiHan = Column(Integer, default=0)
    giaThue = Column(Float, default=0)
    tienCoc = Column(Float, default=0)
    trangThai = Column(SQLEnum(ContractStatus), default=ContractStatus.ACTIVE)
    ngayBatDau = Column(DateTime, default=datetime.utcnow)
    apartment_id = Column(Integer, ForeignKey("apartment.id"))

    apartment = relationship("Apartment", backref=backref("contracts", lazy=True))

# =====================================================
# SERVICE
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
# INVOICE
# =====================================================
class Invoice(BaseModel):
    maHoaDon = Column(String(50), unique=True, nullable=False)
    maHopDong_id = Column(Integer, ForeignKey("contract.id"), nullable=False)
    maHopDong = relationship("Contract", backref="invoices")

    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)
    tienPhong = Column(Float, default=0.0)
    tienDien = Column(Float, default=0.0)
    tienNuoc = Column(Float, default=0.0)
    phuPhiKhac = Column(Float, default=0.0)
    tongCong = Column(Float, default=0.0)
    ngayTaoHoaDon = Column(Date, nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.UNPAID)

    invoice_details = relationship("InvoiceDetail", backref="invoice", lazy=True)

    def __str__(self):
        return self.maHoaDon

# =====================================================
# INVOICE DETAIL
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

# =====================================================
# FUNCTION: LOAD CONTRACTS FROM JSON
# =====================================================
def load_contracts_from_json(file_path="templates/Data/hopDongThue.json"):
    with open(file_path, encoding="utf-8") as f:
        contracts = json.load(f)

    for a in contracts:
        ngayBatDau = datetime.strptime(a["ngayBatDau"], "%d/%m/%Y")
        trangThai_enum = next(
            (status for status in ContractStatus if status.value == a.get("trangThai")),
            ContractStatus.ACTIVE
        )

        contract = Contract(
            maHopDong=a["maHopDong"],
            tenant_name=a["tenant_name"],
            thoiHan=a.get("thoiHan", 0),
            giaThue=a.get("giaThue", 0),
            tienCoc=a.get("tienCoc", 0),
            trangThai=trangThai_enum,
            ngayBatDau=ngayBatDau,
            apartment_id=a.get("apartment_id")
        )
        db.session.add(contract)
    db.session.commit()

# =====================================================
# FUNCTION: LOAD INVOICES FROM JSON
# =====================================================
def load_invoices_from_json(file_path="templates/Data/hoaDon.json"):
    with open(file_path, encoding="utf-8") as f:
        invoices = json.load(f)

    for i in invoices:
        contract = Contract.query.filter_by(maHopDong=i["maHopDong"]).first()
        if not contract:
            continue  # skip if contract doesn't exist

        status_enum = next(
            (s for s in InvoiceStatus if s.value == i.get("status")),
            InvoiceStatus.UNPAID
        )

        invoice = Invoice(
            maHoaDon=i["maHoaDon"],
            maHopDong_id=contract.id,
            thang=i["thang"],
            nam=i["nam"],
            tienPhong=i.get("tienPhong", 0),
            tienDien=i.get("tienDien", 0),
            tienNuoc=i.get("tienNuoc", 0),
            phuPhiKhac=i.get("phuPhiKhac", 0),
            tongCong=i.get("tongCong", 0),
            ngayTaoHoaDon=datetime.strptime(i["ngayTaoHoaDon"], "%Y-%m-%d").date(),
            status=status_enum
        )
        db.session.add(invoice)
    db.session.commit()

# =====================================================
# MAIN: CREATE TABLES + LOAD SAMPLE DATA
# =====================================================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # --- CREATE ADMIN USER ---
        if User.query.count() == 0:
            u = User(
                name="admin",
                username="admin",
                password=hashlib.md5("123456".encode()).hexdigest(),
                user_role=UserRole.ADMIN
            )
            db.session.add(u)
            db.session.commit()

        # --- LOAD APARTMENT TYPES ---
        try:
            with open("templates/Data/apartment_type.json", encoding="utf-8") as f:
                types = json.load(f)
                for t in types:
                    if ApartmentType.query.filter_by(tenLoai=t["tenLoai"]).count() == 0:
                        db.session.add(ApartmentType(**t))
            db.session.commit()
        except Exception as e:
            print("Error loading apartment_type.json:", e)

        # --- LOAD APARTMENTS ---
        try:
            with open("templates/Data/apartment.json", encoding="utf-8") as f:
                apartments = json.load(f)
                for a in apartments:
                    if Apartment.query.filter_by(title=a["title"]).count() == 0:
                        db.session.add(Apartment(**a))
            db.session.commit()
        except Exception as e:
            print("Error loading apartment.json:", e)

        # --- LOAD CONTRACTS ---
        try:
            load_contracts_from_json()
        except Exception as e:
            print("Error loading hopDongThue.json:", e)

        # --- LOAD INVOICES ---
        try:
            load_invoices_from_json()
        except Exception as e:
            print("Error loading hoaDon.json:", e)

        print("Database initialized successfully!")