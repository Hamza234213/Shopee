from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

from config import Config
from models import ensure_settings
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.wallet import wallet_bp
from routes.messages import messages_bp
from routes.buyback import buyback_bp
from routes.invite import invite_bp
from routes.admin import admin_bp

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# Register API blueprints — SIRF EK BAAR
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(products_bp, url_prefix="/api/products")
app.register_blueprint(cart_bp, url_prefix="/api/cart")
app.register_blueprint(orders_bp, url_prefix="/api/orders")
app.register_blueprint(wallet_bp, url_prefix="/api/wallet")
app.register_blueprint(messages_bp, url_prefix="/api/messages")
app.register_blueprint(buyback_bp, url_prefix="/api/buybacks")
app.register_blueprint(invite_bp, url_prefix="/api/invite")
app.register_blueprint(admin_bp, url_prefix="/api/admin")


@app.route("/api/settings", methods=["GET"])
def public_settings():
    from models import settings_col
    s = settings_col.find_one({"_id": "global"}) or {}
    s.pop("_id", None)
    return jsonify(s)


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/admin")
def admin_page():
    return send_from_directory(FRONTEND_DIR, "admin.html")


@app.route("/<path:path>")
def static_files(path):
    full = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(full):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    ensure_settings()
    print("=" * 60)
    print("✅ Bazaro Flask backend starting")
    print("🌐 Frontend:   http://localhost:5000/")
    print("🔐 Admin:      http://localhost:5000/admin")
    print(f"🔑 Password:   {Config.ADMIN_PASSWORD}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)