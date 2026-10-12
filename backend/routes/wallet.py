from datetime import datetime
from flask import Blueprint, request, jsonify
from models import withdrawals_col, deposits_col, users_col, next_id
from utils import auth_required

wallet_bp = Blueprint("wallet", __name__)

@wallet_bp.route("/withdrawals", methods=["POST"])
@auth_required
def request_withdrawal():
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0
    name = str(data.get("name", "")).strip()
    pix_key = str(data.get("pixKey", "")).strip()
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    if not name or not pix_key:
        return jsonify({"error": "Name and PIX key are required"}), 400
    # Brazilian PIX can be a key or an 11-digit CPF.
    if pix_key.isdigit() and len(pix_key) != 11:
        return jsonify({"error": "PIX number must contain 11 digits"}), 400
    user = users_col.find_one({"id": request.user_id})
    if not user or user.get("balance", 0) < amount:
        return jsonify({"error": "Insufficient Balance"}), 400
    w = {
        "id": next_id("withdrawals"),
        "userId": request.user_id,
        "userName": user["name"],
        "name": name,
        "pixKey": pix_key,
        "amount": amount,
        "status": "pending",
        "notification": "Withdrawal request received and is awaiting admin review.",
        "created_at": datetime.utcnow().isoformat(),
    }
    withdrawals_col.insert_one(w)
    w.pop("_id", None)
    return jsonify({"withdrawal": w})

@wallet_bp.route("/withdrawals", methods=["GET"])
@auth_required
def list_withdrawals():
    items = list(withdrawals_col.find({"userId": request.user_id}).sort("id", -1))
    for x in items: x.pop("_id", None)
    return jsonify({"withdrawals": items})

@wallet_bp.route("/deposits", methods=["POST"])
@auth_required
def request_deposit():
    data = request.get_json() or {}
    try: amount = float(data.get("amount", 0))
    except (TypeError, ValueError): amount = 0
    receipt = data.get("receipt", "")
    pix_key = str(data.get("pixKey", "")).strip()
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    if not receipt:
        return jsonify({"error": "Please submit the PIX payment screenshot"}), 400
    user = users_col.find_one({"id": request.user_id})
    d = {
        "id": next_id("deposits"), "userId": request.user_id,
        "userName": user["name"], "amount": amount, "pixKey": pix_key,
        "receipt": receipt, "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    deposits_col.insert_one(d); d.pop("_id", None)
    return jsonify({"deposit": d})

@wallet_bp.route("/deposits", methods=["GET"])
@auth_required
def list_deposits():
    items = list(deposits_col.find({"userId": request.user_id}).sort("id", -1))
    for x in items: x.pop("_id", None)
    return jsonify({"deposits": items})

@wallet_bp.route("/me", methods=["GET"])
@auth_required
def me():
    from routes.auth import public_user
    user = users_col.find_one({"id": request.user_id})
    return jsonify({"user": public_user(user)})
