from models import products_col, ensure_settings, next_id

PRODUCTS = [
    {
        "name": "Logitech Webcam Brio 101 Full HD 1080p Auto Focus",
        "price": 34.99,
        "category": "electronics",
        "icon_key": "webcam",
        "tag": "Hot",
        "image": "https://images.unsplash.com/photo-1611174743420-3d7df880ce32?w=600&q=80&auto=format&fit=crop",
        "description": "Full HD 1080p webcam with auto-light correction, dual mics and privacy shutter."
    },
    {
        "name": "TOMI Ring, Inde Yellow Gold K55 (B324952)",
        "price": 1620.00,
        "category": "jewelry",
        "icon_key": "ring",
        "tag": "New",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600&q=80&auto=format&fit=crop",
        "description": "18K yellow gold ring with natural accent stones."
    },
    {
        "name": "L'ORÉAL Youth Password Serum",
        "price": 89.90,
        "category": "cosmetics",
        "icon_key": "cosmetic_serum",
        "tag": "New",
        "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&q=80&auto=format&fit=crop",
        "description": "Anti-aging serum with hyaluronic acid and vitamin C."
    },
    {
        "name": "Smart Watch Series 8 Pro",
        "price": 399.00,
        "category": "watches",
        "icon_key": "watch_smart",
        "tag": "Hot",
        "image": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&q=80&auto=format&fit=crop",
        "description": "AMOLED display, heart-rate monitor, GPS and 7-day battery life."
    },
    {
        "name": "Classic Leather Watch Brown",
        "price": 249.00,
        "category": "watches",
        "icon_key": "watch_leather",
        "tag": "Sale",
        "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=600&q=80&auto=format&fit=crop",
        "description": "Timeless brown leather strap watch."
    },
    {
        "name": "Cadeira de rodas de transporte leve e dobrável",
        "price": 1220.00,
        "category": "home",
        "icon_key": "travelbed",
        "image": "https://images.unsplash.com/photo-1587293852726-70cdb56c2866?w=600&q=80&auto=format&fit=crop",
        "description": "Lightweight foldable transport wheelchair."
    },
    {
        "name": "Android 13.0 Radio for Toyota Etios 2010-2019",
        "price": 3280.00,
        "category": "electronics",
        "icon_key": "device_cat",
        "image": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=600&q=80&auto=format&fit=crop",
        "description": "13.0 inch IPS Touch Screen Stereo with Bluetooth 5.0, Carplay, Android Auto GPS."
    },
    {
        "name": "Oura Ring 5 Smart Ring Monitor",
        "price": 3300.00,
        "category": "jewelry",
        "icon_key": "ring",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600&q=80&auto=format&fit=crop",
        "description": "Smart ring monitor with sleep tracking and health insights."
    },
    {
        "name": "Brown Tweezers BT Skin Powder Matte Loose",
        "price": 137.00,
        "category": "cosmetics",
        "icon_key": "cosmetic_cream",
        "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&q=80&auto=format&fit=crop",
        "description": "Matte loose powder for oily and combination skin."
    },
    {
        "name": "La Mer The Concentrate (50ml)",
        "price": 25.00,
        "category": "cosmetics",
        "icon_key": "cosmetic_serum",
        "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&q=80&auto=format&fit=crop",
        "description": "Soothing concentrate for sensitive skin."
    },
    {
        "name": "Hiccapop Inflatable Toddler Travel Bed",
        "price": 60.00,
        "category": "home",
        "icon_key": "travelbed",
        "tag": "Hot",
        "image": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&q=80&auto=format&fit=crop",
        "description": "Portable toddler bed for travel, camping and vacation."
    },
]


def seed():
    ensure_settings()
    if products_col.count_documents({}) > 0:
        print(f"⚠️  Products already exist ({products_col.count_documents({})}). Skipping seed.")
        return
    for p in PRODUCTS:
        p["id"] = next_id("products")
        products_col.insert_one(p)
        print(f"✅ Inserted: {p['name'][:50]}")
    print(f"\n🎉 Seeded {len(PRODUCTS)} products into MongoDB.")


if __name__ == "__main__":
    seed()