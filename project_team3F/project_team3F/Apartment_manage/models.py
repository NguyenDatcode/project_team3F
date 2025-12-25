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



class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)



class User(BaseModel, UserMixin):
    __tablename__ = "user"

    name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    avatar = Column(String(255))
    user_role = Column(SQLEnum(UserRole), default=UserRole.USER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"<User {self.username}>"



class ApartmentType(BaseModel):
    __tablename__ = "apartment_type"

    tenLoai = Column(String(100), nullable=False)
    giaCoBan = Column(Float, default=0.0)
    dienTich = Column(Float, default=0.0)
    moTa = Column(Text)

    apartments = relationship("Apartment", backref="type", lazy=True)

    def __str__(self):
        return self.tenLoai


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
    trangThai = Column(String(50), default="Đang áp dụng")
    invoice_details = relationship("InvoiceDetail", backref="service", lazy=True)

    def __str__(self):
        return self.tenDichVu

#========INVOICE======
class Invoice(BaseModel):
    __tablename__ = "invoice"

    maHoaDon = Column(String(50), unique=True, nullable=False)

    maHopDong_id = Column(Integer, ForeignKey("contract.id"), nullable=False)
    maHopDong = relationship("Contract", backref="invoices")

    regulation_id = Column(Integer, ForeignKey("regulation.id"), nullable=False)
    regulation = relationship("Regulation")

    thang = Column(Integer, nullable=False)
    nam = Column(Integer, nullable=False)

    tienPhong = Column(Float, default=0)
    tienDien = Column(Float, default=0)
    tienNuoc = Column(Float, default=0)
    phuPhiKhac = Column(Float, default=0)
    tongCong = Column(Float, default=0)

    ngayTaoHoaDon = Column(Date, nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.UNPAID)

    invoice_details = relationship("InvoiceDetail", backref="invoice", lazy=True)

    def __str__(self):
        return self.maHoaDon



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


# ================== REGULATION ==================

class Regulation(BaseModel):
    __tablename__ = "regulation"

    maQuyDinh = Column(String(50), unique=True, nullable=False)
    tenQuyDinh = Column(String(255), nullable=False)

    giaDien = Column(Float, nullable=False)
    giaNuoc = Column(Float, nullable=False)
    phiDichVu = Column(Float, default=0)
    soNguoiToiDa = Column(Integer, default=2)
    phiTreHan = Column(Float, default=0)

    ngayBatDau = Column(Date, nullable=False)
    ngayKetThuc = Column(Date)

    ghiChu = Column(Text)

    def __str__(self):
        return self.tenQuyDinh

class ContactMessage(BaseModel):
        __tablename__ = 'contact_messages'

        name = Column(String(100), nullable=False)
        email = Column(String(100), nullable=False)
        subject = Column(String(150), nullable=False)
        message = Column(Text, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f"<ContactMessage(name='{self.name}', email='{self.email}', subject='{self.subject}')>"



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


def load_regulations_from_json(file_path="templates/Data/quyDinh.json"):
    with open(file_path, encoding="utf-8") as f:
        regulations = json.load(f)

    for r in regulations:
        regulation = Regulation(
            maQuyDinh=r["maQuyDinh"],
            tenQuyDinh=r["tenQuyDinh"],
            giaDien=float(r["giaDien"]),
            giaNuoc=float(r["giaNuoc"]),
            phiDichVu=float(r.get("phiDichVu", 0)),
            soNguoiToiDa=int(r.get("soNguoiToiDa", 2)),
            phiTreHan=float(r.get("phiTreHan", 0)),
            ngayBatDau=datetime.strptime(r["ngayBatDau"], "%Y-%m-%d").date(),
            ngayKetThuc=datetime.strptime(r["ngayKetThuc"], "%Y-%m-%d").date()
                if r.get("ngayKetThuc") else None,
            ghiChu=r.get("ghiChu", "")
        )
        db.session.add(regulation)

    db.session.commit()


def load_invoices_from_json(file_path="templates/Data/hoaDon.json"):
    with open(file_path, encoding="utf-8") as f:
        invoices = json.load(f)

    for i in invoices:
        contract = Contract.query.filter_by(maHopDong=i["maHopDong"]).first()
        if not contract:
            print(f"Không tìm thấy hợp đồng {i['maHopDong']}")
            continue

        regulation = Regulation.query.filter_by(
            maQuyDinh=i["regulation"]
        ).first()
        if not regulation:
            print(f"Không tìm thấy quy định {i['regulation']}")
            continue

        status_enum = next(
            (s for s in InvoiceStatus if s.name == i.get("status")),
            InvoiceStatus.UNPAID
        )

        invoice = Invoice(
            maHoaDon=i["maHoaDon"],
            maHopDong_id=contract.id,
            regulation_id=regulation.id,

            thang=i["thang"],
            nam=i["nam"],

            tienPhong=i.get("tienPhong", 0),
            tienDien=i.get("tienDien", 0),
            tienNuoc=i.get("tienNuoc", 0),
            phuPhiKhac=i.get("phuPhiKhac", 0),
            tongCong=i.get("tongCong", 0),

            ngayTaoHoaDon=datetime.strptime(
                i["ngayTaoHoaDon"], "%Y-%m-%d"
            ).date(),
            status=status_enum
        )

        db.session.add(invoice)

    db.session.commit()


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


        # ----LOAD REGULATONS-----
        try:
            load_regulations_from_json()
        except Exception as e:
            print("Error loading quyDinh.json:", e)


        # --- LOAD INVOICES ---
        try:
            load_invoices_from_json()
        except Exception as e:
            print("Error loading hoaDon.json:", e)

        print("Database initialized successfully!")

        # --- LOAD SERVICES ---
        try:
            with open("templates/Data/dichVu.json", encoding="utf-8") as f:
                types = json.load(f)
                for t in types:
                    if Service.query.filter_by(maDichVu=t["maDichVu"]).count() == 0:
                        db.session.add(Service(**t))
            db.session.commit()
        except Exception as e:
            print("Error loading apartment_type.json:", e)