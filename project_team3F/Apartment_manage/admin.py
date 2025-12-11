from Apartment_manage import dao
from Apartment_manage.dao import get_all_apartments
from flask import Blueprint, render_template,request,jsonify
from database import get_all_apartments, get_all_apartment_types

admin_bp = Blueprint("admin", __name__, template_folder="templates/admin", url_prefix="/admin")

# UI pages (render HTML)
@admin_bp.route("/apartments")
def apartments_page():
    types = dao.get_all_apartment_types()
    return render_template("admin/apartments.html", types=types)

@admin_bp.route("/apartment-types")
def apartment_types_page():
    return render_template("admin/apartment_types.html")

# API JSON endpoints for Apartments
@admin_bp.route("/api/apartments", methods=["GET"])
def api_list_apartments():
    apartments = dao.get_all_apartments()
    data = []
    for a in apartments:
        data.append({
            "id": a.id,
            "title": a.title,
            "price": a.price,
            "status": a.status,
            "apartment_type": a.apartment_type.name if a.apartment_type else None,
            "apartment_type_id": a.apartment_type_id,
            "location": a.location
        })
    return jsonify(data)

@admin_bp.route("/api/apartments", methods=["POST"])
def api_create_apartment():
    data = request.json or {}
    try:
        a = dao.create_apartment(
            title=data.get("title"),
            price=data.get("price", 0),
            area=data.get("area"),
            bedrooms=data.get("bedrooms", 1),
            bathrooms=data.get("bathrooms", 1),
            floor=data.get("floor", 1),
            status=data.get("status", "available"),
            location=data.get("location"),
            is_vip=bool(data.get("is_vip", False)),
            description_short=data.get("description_short"),
            image_url=data.get("image_url"),
            apartment_type_id=data.get("apartment_type_id")
        )
        return jsonify({"success": True, "id": a.id})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 400

@admin_bp.route("/api/apartments/<int:ap_id>", methods=["PUT"])
def api_update_apartment(ap_id):
    data = request.json or {}
    a = dao.update_apartment(ap_id, **data)
    if not a:
        return jsonify({"success": False, "error": "Not found"}), 404
    return jsonify({"success": True})

@admin_bp.route("/api/apartments/<int:ap_id>", methods=["DELETE"])
def api_delete_apartment(ap_id):
    ok = dao.delete_apartment(ap_id)
    return jsonify({"success": ok})

# API for Apartment Types
@admin_bp.route("/api/types", methods=["GET"])
def api_list_types():
    types = dao.get_all_apartment_types()
    return jsonify([{"id": t.id, "name": t.name, "base_price": t.base_price, "area_default": t.area_default} for t in types])

@admin_bp.route("/api/types", methods=["POST"])
def api_create_type():
    data = request.json or {}
    try:
        t = dao.create_apartment_type(
            name=data.get("name"),
            base_price=float(data.get("base_price", 0) or 0),
            area_default=float(data.get("area_default", 0) or 0),
            description=data.get("description")
        )
        return jsonify({"success": True, "id": t.id})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)}), 400

@admin_bp.route("/api/types/<int:type_id>", methods=["PUT"])
def api_update_type(type_id):
    data = request.json or {}
    t = dao.update_apartment_type(type_id, **data)
    if not t:
        return jsonify({"success": False, "error": "Not found"}), 404
    return jsonify({"success": True})

@admin_bp.route("/api/types/<int:type_id>", methods=["DELETE"])
def api_delete_type(type_id):
    ok = dao.delete_apartment_type(type_id)
    return jsonify({"success": ok})


@admin.route('/admin/apartment')
def apartment_list():
    data = get_all_apartments()
    return render_template('admin/apartment_list.html', apartments=data)


@admin.route('/admin/apartment_type')
def apartment_type_list():
    data = get_all_apartment_types()
    return render_template('admin/apartment_type_list.html', types=data)
