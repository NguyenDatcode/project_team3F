import hashlib
import json
import os
from datetime import datetime, timedelta, date
from operator import or_

# from mediapipe.calculators import image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import cloudinary.uploader
# from scipy.special._precompute.cosine_cdf import q
from sqlalchemy import extract, func
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from Apartment_manage.app import app
from Apartment_manage.models import Apartment, ApartmentType, Contract, User, Service, Regulation, ContractStatus, \
    Invoice, InvoiceDetail, UserRole, InvoiceStatus
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


def get_all_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return [{
        "id": u.id,
        "name": u.name,
        "username": u.username,
        "user_role": u.user_role.name,
        "active": u.active,
        "created_at": u.created_at.strftime("%d/%m/%Y")
    } for u in users]


def get_user_detail(user_id):
    u = User.query.get_or_404(user_id)
    return {
        "id": u.id,
        "name": u.name,
        "username": u.username,
        "user_role": u.user_role.name,
        "active": u.active,
        "created_at": u.created_at.strftime("%d/%m/%Y"),
        "avatar": u.avatar
    }


def create_user(data):
    if User.query.filter_by(username=data["username"]).first():
        raise Exception("Username đã tồn tại")

    password = hashlib.md5(data["password"].encode()).hexdigest()

    u = User(
        name=data["name"],
        username=data["username"],
        password=password,
        user_role=UserRole[data["user_role"]],
        active=True
    )
    db.session.add(u)
    db.session.commit()


def update_user(user_id, data):
    u = User.query.get_or_404(user_id)

    u.name = data["name"]
    u.user_role = UserRole[data["user_role"]]
    u.active = data["active"]

    if data.get("password"):
        u.password = hashlib.md5(data["password"].encode()).hexdigest()

    db.session.commit()


def delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()


# def toggle_user_active(user_id):
#     user = User.query.get_or_404(user_id)
#     user.is_active = not user.is_active
#     db.session.commit()

def reset_password(user_id, new_pw="123456"):
    user = User.query.get_or_404(user_id)
    user.set_password(new_pw)
    db.session.commit()

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
    image_url = upload_image(image)

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


            #===========SERVICES==========

def get_all_services():
    return Service.query.all()


def get_all_services_json():
    services = Service.query.all()
    return [{
        "id": s.id,
        "maDichVu": s.maDichVu,
        "tenDichVu": s.tenDichVu,
        "donGia": s.donGia,
        "donViTinh": s.donViTinh,
        "loaiTinhPhi": s.loaiTinhPhi,
        "active": s.active
    } for s in services]

def get_service_id(ma_dich_vu: str):
    if not ma_dich_vu:
        return None

    service = Service.query.filter_by(maDichVu=ma_dich_vu).first()

    if not service:
        print(f"Không tìm thấy dịch vụ: {ma_dich_vu}")
        return None

    return service.id


def add_service(data):
    service = Service(
        maDichVu=data["maDichVu"],
        tenDichVu=data["tenDichVu"],
        donGia=float(data["donGia"]),
        donViTinh=data.get("donViTinh"),
        loaiTinhPhi=data.get("loaiTinhPhi")
    )
    db.session.add(service)
    db.session.commit()


def update_service(service_id, data):
    s = Service.query.get_or_404(service_id)

    s.tenDichVu = data["tenDichVu"]
    s.donGia = float(data["donGia"])
    s.donViTinh = data.get("donViTinh")
    s.loaiTinhPhi = data.get("loaiTinhPhi")

    db.session.commit()


def delete_service(service_id):
    s = Service.query.get_or_404(service_id)
    s.active = False
    if s:
        db.session.delete(s)
        db.session.commit()


        #======= CONTRACT ==========
def get_all_contracts():
    contracts = Contract.query \
        .options(joinedload(Contract.apartment)) \
        .order_by(Contract.id.desc()) \
        .all()

    result = []
    for c in contracts:
        result.append({
            "id": c.id,
            "maHopDong": c.maHopDong,
            "tenant_name": c.tenant_name,
            "thoiHan": c.thoiHan,
            "giaThue": c.giaThue,
            "tienCoc": c.tienCoc,
            "trangThai": c.trangThai.value,
            "ngayBatDau": c.ngayBatDau.strftime("%Y-%m-%d"),
            "apartment": {
                "id": c.apartment.id,
                "title": c.apartment.title
            } if c.apartment else None
        })
    return result

def is_apartment_available(apartment_id):
    active_contract = Contract.query.filter(
        Contract.apartment_id == apartment_id,
        Contract.trangThai == ContractStatus.ACTIVE
    ).first()

    return active_contract is None


def add_contract(data):
    # Validate
    required_fields = ["maHopDong", "tenant_name", "apartment_id", "giaThue"]
    for f in required_fields:
        if not data.get(f):
            raise ValueError(f"Thiếu dữ liệu: {f}")

    apartment = Apartment.query.get(int(data["apartment_id"]))
    if not apartment:
        raise ValueError("Căn hộ không tồn tại")

    contract = Contract(
        maHopDong=data["maHopDong"],
        tenant_name=data["tenant_name"],
        thoiHan=int(data.get("thoiHan", 0)),
        giaThue=float(data["giaThue"]),
        tienCoc=float(data.get("tienCoc", 0)),
        apartment_id=apartment.id,
        trangThai=ContractStatus.ACTIVE,
        ngayBatDau=datetime.strptime(
            data.get("ngayBatDau"), "%Y-%m-%d"
        ) if data.get("ngayBatDau") else datetime.utcnow()
    )

    db.session.add(contract)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Mã hợp đồng đã tồn tại")


def get_contract_by_id(contract_id):
    c = Contract.query.get_or_404(contract_id)

    return {
        "id": c.id,
        "maHopDong": c.maHopDong,
        "tenant_name": c.tenant_name,
        "thoiHan": c.thoiHan,
        "giaThue": c.giaThue,
        "tienCoc": c.tienCoc,
        "trangThai": c.trangThai.value,
        "ngayBatDau": c.ngayBatDau.strftime("%Y-%m-%d"),
        "apartment_id": c.apartment_id
    }


def update_contract(contract_id, data):
    contract = Contract.query.get_or_404(contract_id)
    contract = Contract.query.get_or_404(contract_id)

    contract.tenant_name = data.get("tenant_name", contract.tenant_name)
    contract.thoiHan = int(data.get("thoiHan", contract.thoiHan))
    contract.giaThue = float(data.get("giaThue", contract.giaThue))
    contract.tienCoc = float(data.get("tienCoc", contract.tienCoc))

    if data.get("trangThai"):
        # Lấy enum theo giá trị
        value = data.get("trangThai")
        try:
            contract.trangThai = next(s for s in ContractStatus if s.value == value)
        except StopIteration:
            raise ValueError(f"Trạng thái hợp đồng không hợp lệ: {value}")

    if data.get("apartment_id"):
        contract.apartment_id = int(data.get("apartment_id"))

    if data.get("ngayBatDau"):
        contract.ngayBatDau = datetime.strptime(
            data["ngayBatDau"], "%Y-%m-%d"
        )

    db.session.commit()
    db.session.commit()

def delete_contract(contract_id):
    contract = Contract.query.get(contract_id)
    if not contract:
        return False

    # Nếu đã có hóa đơn → không cho xóa
    if contract.invoices:
        raise ValueError("Không thể xóa hợp đồng đã phát sinh hóa đơn")

    db.session.delete(contract)
    db.session.commit()
    return True

        #========REGULATIONS=======

def get_all_regulations():
    return Regulation.query.order_by(Regulation.ngayBatDau.desc()).all()


def add_regulation(data):
    r = Regulation(
        maQuyDinh=data["maQuyDinh"],
        tenQuyDinh=data["tenQuyDinh"],
        giaDien=float(data["giaDien"]),
        giaNuoc=float(data["giaNuoc"]),
        phiDichVu=float(data.get("phiDichVu", 0)),
        soNguoiToiDa=int(data.get("soNguoiToiDa", 2)),
        phiTreHan=float(data.get("phiTreHan", 0)),
        ngayBatDau=datetime.strptime(data["ngayBatDau"], "%Y-%m-%d").date(),
        ngayKetThuc=datetime.strptime(data["ngayKetThuc"], "%Y-%m-%d").date()
            if data.get("ngayKetThuc") else None,
        ghiChu=data.get("ghiChu", "")
    )

    db.session.add(r)
    db.session.commit()


def update_regulation(rid, data):
    r = Regulation.query.get_or_404(rid)

    r.maQuyDinh = data["maQuyDinh"]
    r.tenQuyDinh = data["tenQuyDinh"]
    r.giaDien = float(data["giaDien"])
    r.giaNuoc = float(data["giaNuoc"])
    r.phiDichVu = float(data.get("phiDichVu", 0))
    r.soNguoiToiDa = int(data.get("soNguoiToiDa", 2))
    r.phiTreHan = float(data.get("phiTreHan", 0))
    r.ngayBatDau = datetime.strptime(data["ngayBatDau"], "%Y-%m-%d").date()
    r.ngayKetThuc = datetime.strptime(data["ngayKetThuc"], "%Y-%m-%d").date() \
        if data.get("ngayKetThuc") else None
    r.ghiChu = data.get("ghiChu", "")

    db.session.commit()


def delete_regulation(rid):
    r = Regulation.query.get(rid)
    if r:
        db.session.delete(r)
        db.session.commit()

def get_active_regulation(at_date=None):
    if not at_date:
        at_date = date.today()

    return Regulation.query.filter(
        Regulation.ngayBatDau <= at_date,
        or_(
            Regulation.ngayKetThuc == None,
            Regulation.ngayKetThuc >= at_date
        )
    ).order_by(Regulation.ngayBatDau.desc()).first()

        #======INVOICES======
def get_all_invoices(month=None, year=None, status=None):
    query = Invoice.query.options(
        joinedload(Invoice.maHopDong)
    )

    if month:
        query = query.filter(Invoice.thang == month)

    if year:
        query = query.filter(Invoice.nam == year)

    if status:
        query = query.filter(Invoice.status == InvoiceStatus[status])

    invoices = query.order_by(Invoice.ngayTaoHoaDon.desc()).all()

    return [{
        "id": i.id,
        "maHoaDon": i.maHoaDon,
        "hopDong": i.maHopDong.maHopDong,
        "thang": i.thang,
        "nam": i.nam,
        "tongCong": i.tongCong,
        "status": i.status.value,
        "ngayTaoHoaDon": i.ngayTaoHoaDon.strftime("%d/%m/%Y")
    } for i in invoices]


def get_invoice_detail(invoice_id):
    invoice = Invoice.query.options(
        joinedload(Invoice.invoice_details)
        .joinedload(InvoiceDetail.service),
        joinedload(Invoice.maHopDong)
    ).get_or_404(invoice_id)

    return {
        "maHoaDon": invoice.maHoaDon,
        "hopDong": invoice.maHopDong.maHopDong,
        "thang": invoice.thang,
        "nam": invoice.nam,
        "status": invoice.status.value,
        "tongCong": invoice.tongCong,
        "items": [{
            "tenDichVu": d.service.tenDichVu,
            "moTa": d.moTa,
            "donGia": d.donGiaApDung,
            "soLuong": d.soLuong,
            "thanhTien": d.thanhTien
        } for d in invoice.invoice_details]
    }


def generate_monthly_invoices(thang, nam):
    contracts = Contract.query.filter(
        Contract.trangThai == ContractStatus.ACTIVE
    ).all()

    regulation = get_active_regulation(date(nam, thang, 1))
    if not regulation:
        raise Exception("Không có quy định hiệu lực")

    for c in contracts:
        exists = Invoice.query.filter_by(
            maHopDong_id=c.id,
            thang=thang,
            nam=nam
        ).first()
        if exists:
            continue

        maHoaDon = f"HD-{c.maHopDong}-{thang}-{nam}"

        invoice = Invoice(
            maHoaDon=maHoaDon,
            maHopDong_id=c.id,
            regulation_id=regulation.id,
            thang=thang,
            nam=nam,
            tienPhong=c.giaThue,
            phuPhiKhac=regulation.phiDichVu,
            ngayTaoHoaDon=date.today()
        )

        db.session.add(invoice)
        db.session.flush()

        total = invoice.tienPhong + invoice.phuPhiKhac

        # ===== ĐIỆN =====
        service_dien = Service.query.filter_by(maDichVu="DV04").first()
        if service_dien:
            detail = InvoiceDetail(
                maCTHD=f"CT-{invoice.id}-DIEN",
                maHoaDon_id=invoice.id,
                maDichVu_id=service_dien.id,
                moTa="Tiền điện",
                donGiaApDung=regulation.giaDien,
                soLuong=1,
                thanhTien=regulation.giaDien
            )
            total += detail.thanhTien
            db.session.add(detail)

        invoice.tongCong = total

    db.session.commit()

def mark_invoice_paid(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if invoice.status.value == "Đã thanh toán":
        return
    invoice.status = "PAID"
    db.session.commit()

def export_invoice_pdf(invoice_id):
    invoice = Invoice.query.get(invoice_id)

    path = f"static/invoices/{invoice.maHoaDon}.pdf"
    c = canvas.Canvas(path, pagesize=A4)

    c.drawString(50, 800, f"HÓA ĐƠN {invoice.maHoaDon}")
    c.drawString(50, 770, f"Tổng tiền: {invoice.tongCong}")

    y = 740
    for d in invoice.invoice_details:
        c.drawString(50, y, f"{d.service.tenDichVu} - {d.thanhTien}")
        y -= 20

    c.save()
    return path


def calculate_invoice_details(invoice, chi_tiet_list):
    """
    Tạo InvoiceDetail cho 1 hóa đơn
    """
    total = 0

    for item in chi_tiet_list:
        service_id = get_service_id(item["maDichVu"])

        if not service_id:
            continue  # bỏ qua dịch vụ không tồn tại

        detail = InvoiceDetail(
            maCTHD=item["maCTHD"],
            invoice_id=invoice.id,
            service_id=service_id,
            moTa=item.get("moTa"),
            chiSoCu=item.get("chiSoCu"),
            chiSoMoi=item.get("chiSoMoi"),
            donGiaApDung=item.get("donGiaApDung", 0),
            soLuong=item.get("soLuong", 1),
            thanhTien=item.get("thanhTien", 0)
        )

        total += detail.thanhTien
        db.session.add(detail)

    return total


        #=======REPORT-THỐNG KÊ======

def stat_apartment_status():
    total = Apartment.query.count()

    active_contract_apts = db.session.query(Apartment.id)\
        .join(Contract)\
        .filter(Contract.trangThai == ContractStatus.ACTIVE)\
        .distinct().count()

    return {
        "dangThue": active_contract_apts,
        "trong": total - active_contract_apts
    }


def stat_revenue_by_year(year):
    rows = db.session.query(
        extract("month", Invoice.ngayTaoHoaDon).label("month"),
        func.sum(Invoice.tongCong)
    ).filter(
        extract("year", Invoice.ngayTaoHoaDon) == year,
        Invoice.status == InvoiceStatus.PAID
    ).group_by("month").all()

    data = {int(m): float(t) for m, t in rows}

    return [
        data.get(m, 0) for m in range(1, 13)
    ]


def stat_contract_expiring(days=30):
    today = datetime.today()
    limit = today + timedelta(days=days)

    contracts = Contract.query.filter(
        Contract.trangThai == ContractStatus.ACTIVE,
        Contract.ngayBatDau + func.make_interval(0,0,0,0,0,0,0) != None
    ).all()

    result = []
    for c in contracts:
        end_date = c.ngayBatDau + timedelta(days=c.thoiHan * 30)
        if today <= end_date <= limit:
            result.append({
                "maHopDong": c.maHopDong,
                "tenant": c.tenant_name,
                "endDate": end_date.strftime("%d/%m/%Y")
            })

    return result
from flask import request

def load_type(q=None, type_id=None, page=None):
    # with open("data/product.json", encoding="utf-8") as f:
    #     products = json.load(f)
    #
    #     if q:
    #         products = [p for p in products if p["name"].find(q)>=0]
    #
    #     if cate_id:
    #         products = [p for p in products if p["cate_id"].__eq__(int(cate_id))]
    #
    #     return products
    query =Apartment.query

    if q:
        query = query.filter(Apartment.title.contains(q))

    if type_id:
        query = query.filter(Apartment.type_id.__eq__(type_id))

    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page)-1)*size
        query = query.slice(start, start+size)

    return query.all()

def upload_image(file, folder="apartments"):
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type="image"
    )
    return result["secure_url"]