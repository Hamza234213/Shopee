from datetime import datetime
from flask import Blueprint, request, jsonify
from models import orders_col, carts_col, products_col, users_col, next_id
from utils import auth_required

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("", methods=["GET"])
@auth_required
def list_orders():
    items = list(orders_col.find({"userId": request.user_id}).sort("id", -1))
    for o in items: o.pop("_id", None)
    return jsonify({"orders": items})

@orders_bp.route("", methods=["POST"])
@auth_required
def create_order():
    body = request.get_json() or {}
    direct_items = body.get("items")
    if direct_items:
        source_items = direct_items
    else:
        cart = carts_col.find_one({"userId": request.user_id}) or {"items": []}
        source_items = cart.get("items", [])
    if not source_items:
        return jsonify({"error": "Cart is empty"}), 400

    order_items, total = [], 0
    for ci in source_items:
        try: pid, qty = int(ci["productId"]), int(ci.get("qty", 1))
        except (KeyError, TypeError, ValueError): continue
        if qty < 1: continue
        p = products_col.find_one({"id": pid})
        if not p: continue
        order_items.append({"product_id": p["id"], "name": p["name"], "price": p["price"], "qty": qty})
        total += float(p["price"]) * qty
    if not order_items:
        return jsonify({"error": "Product not found"}), 404

    user = users_col.find_one({"id": request.user_id})
    if not user or user.get("balance", 0) < total:
        return jsonify({"error": "Insufficient Balance"}), 400

    users_col.update_one({"id": request.user_id}, {"$inc": {"balance": -total}})
    order = {
        "id": next_id("orders"), "userId": request.user_id, "items": order_items,
        "total": round(total, 2), "status": "placed",
        "created_at": datetime.utcnow().isoformat(),
    }
    orders_col.insert_one(order)
    if not direct_items:
        carts_col.update_one({"userId": request.user_id}, {"$set": {"items": []}})
    order.pop("_id", None)
    from routes.auth import public_user
    user = users_col.find_one({"id": request.user_id})
    return jsonify({"order": order, "user": public_user(user)})
