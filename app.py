from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "sandesh-dev-secret")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")
CATEGORY_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".avif")
CATEGORY_IMAGE_FILENAMES = {
    "Bengali Sweets": "images/bengalisweets_mc.jpg",
    "Dry Fruit Sweets": "images/dryfruitsweets_mc.jpg",
    "Barfi": "images/barfi_mc.jpg",
    "Mawa Barfi": "images/mawabarfi_mc.jpg",
    "Pedha": "images/pedha_mc.jpg",
    "Laddu": "images/laddu_mc.jpg",
    "Halwa": "images/halwa_mc.png",
    "Sonpapdi": "images/SoanPapdi_mc.jpg",
    "Snacks": "images/snacks_mc.jpg",
}

CATEGORY_ORDER = [
    "Bengali Sweets",
    "Dry Fruit Sweets",
    "Barfi",
    "Mawa Barfi",
    "Pedha",
    "Laddu",
    "Halwa",
    "Sonpapdi",
    "Snacks",
]

POPULAR_HERO_PRODUCTS = [
    "Gulabjamun",
    "Kaju Katali",
    "Rasgulla",
]


CATEGORY_DETAILS = {
    "Bengali Sweets": {
        "desc": "Soft, syrupy Bengali mithai and milk-based favorites.",
        "theme": "bengali",
        "image_url": "/static/images/gulabjamun.jpg",
        "image_position": "center 72%",
        "image_size": "120%",
    },
    "Dry Fruit Sweets": {
        "desc": "Rich kaju, anjeer and festive premium selections.",
        "theme": "dryfruit",
        "image_url": "/static/images/kajukatli.jpg",
        "image_position": "80% 78%",
        "image_size": "132%",
    },
    "Barfi": {
        "desc": "Classic barfi varieties for everyday and gifting orders.",
        "theme": "barfi",
        "image_url": "https://images.unsplash.com/photo-1633945274309-2c16c9682a8b?auto=format&fit=crop&w=1200&q=80",
        "image_position": "center 70%",
        "image_size": "134%",
    },
    "Mawa Barfi": {
        "desc": "Dense mawa sweets with chocolate and pista flavors.",
        "theme": "mawa",
        "image_url": "https://images.unsplash.com/photo-1633945274309-2c16c9682a8b?auto=format&fit=crop&w=1200&q=80",
        "image_position": "center 72%",
        "image_size": "126%",
    },
    "Pedha": {
        "desc": "Soft pedha options in regular, small and white varieties.",
        "theme": "pedha",
        "image_url": "https://images.unsplash.com/photo-1666190092159-3171cf0fbb12?auto=format&fit=crop&w=1200&q=80",
        "image_position": "center 62%",
        "image_size": "122%",
    },
    "Laddu": {
        "desc": "Traditional laddu picks from besan to pure ghee specials.",
        "theme": "laddu",
        "image_url": "https://images.unsplash.com/photo-1666190092159-3171cf0fbb12?auto=format&fit=crop&w=1200&q=80",
        "image_position": "center 84%",
        "image_size": "124%",
    },
    "Halwa": {
        "desc": "Halwa favorites from badam to ghee-rich seasonal styles.",
        "theme": "halwa",
        "image_url": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=1200&q=80",
        "image_position": "center 72%",
        "image_size": "122%",
    },
    "Sonpapdi": {
        "desc": "Flaky sonpapdi and desi sweet classics like balushahi.",
        "theme": "sonpapdi",
        "image_url": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=1200&q=80",
        "image_position": "center 62%",
        "image_size": "122%",
    },
    "Snacks": {
        "desc": "Hot and savory quick bites like samosa and jalebi.",
        "theme": "snacks",
        "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?auto=format&fit=crop&w=1200&q=80",
        "image_position": "72% 54%",
        "image_size": "124%",
    },
}

FEATURED_PRODUCT_IMAGES = {
    "Gulabjamun": {
        "image_url": "/static/images/gulabjamun.jpg",
        "image_alt": "Gulab jamun served in a bowl",
    },
    "Kaju Katali": {
        "image_url": "/static/images/kajukatli.jpg",
        "image_alt": "Kaju katli pieces arranged on a tray",
    },
    "Malai Barfi": {
        "image_url": "https://images.unsplash.com/photo-1633945274309-2c16c9682a8b?auto=format&fit=crop&w=900&q=80",
        "image_alt": "Barfi sweet pieces on a platter",
    },
    "Chocolate Mawa Barfi": {
        "image_url": "https://images.unsplash.com/photo-1633945274309-2c16c9682a8b?auto=format&fit=crop&w=900&q=80",
        "image_alt": "Rich mawa barfi pieces",
    },
    "Malai Pedha (Regular Size)": {
        "image_url": "https://images.unsplash.com/photo-1666190092159-3171cf0fbb12?auto=format&fit=crop&w=900&q=80",
        "image_alt": "Pedha sweets arranged for serving",
    },
    "Besan Laddu": {
        "image_url": "https://images.unsplash.com/photo-1666190092159-3171cf0fbb12?auto=format&fit=crop&w=900&q=80",
        "image_alt": "Traditional laddu sweets",
    },
    "Badam Halwa": {
        "image_url": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=900&q=80",
        "image_alt": "Halwa served in a bowl",
    },
    "Sonpapdi": {
        "image_url": "https://images.unsplash.com/photo-1617093727343-374698b1b08d?auto=format&fit=crop&w=900&q=80",
        "image_alt": "Flaky sweet pieces served neatly",
    },
    "Samosa": {
        "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?auto=format&fit=crop&w=900&q=80",
        "image_alt": "Fresh samosas served hot",
    },
}


def apply_product_image(product):
    featured_image = FEATURED_PRODUCT_IMAGES.get(product["name"])
    product["featured"] = bool(featured_image)

    if featured_image:
        product["image_url"] = featured_image["image_url"]
        product["image_alt"] = featured_image["image_alt"]
    elif product.get("image"):
        product["image_url"] = url_for("static", filename=product["image"])
        product["image_alt"] = product["name"]
    else:
        product.pop("image_url", None)
        product.pop("image_alt", None)
        product.pop("photographer_name", None)
        product.pop("photographer_link", None)


def build_hero_promos(products):
    products_by_name = {product["name"]: product for product in products}
    promos = []

    for product_name in POPULAR_HERO_PRODUCTS:
        product = products_by_name.get(product_name)
        if not product or not product.get("image_url"):
            continue

        promos.append(
            {
                "name": product["name"],
                "price": product["price"],
                "unit": product["unit"],
                "image_url": product["image_url"],
                "image_alt": product.get("image_alt") or product["name"],
                "category_slug": slugify(product["category"]),
            }
        )

    return promos


def load_products():
    json_path = os.path.join(app.root_path, "products.json")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    return []


def save_products(products):
    json_path = os.path.join(app.root_path, "products.json")

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)
        file.write("\n")


def slugify(text):
    return (
        text.lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
    )


def resolve_image_url(image_path):
    if not image_path:
        return None

    if image_path.startswith(("http://", "https://", "/")):
        return image_path

    return url_for("static", filename=image_path)


def get_category_image_url(category_name):
    slug = slugify(category_name)

    for extension in CATEGORY_IMAGE_EXTENSIONS:
        relative_path = f"images/categories/{slug}{extension}"
        absolute_path = os.path.join(app.static_folder, relative_path)

        if os.path.exists(absolute_path):
            return url_for("static", filename=relative_path)

    legacy_relative_path = CATEGORY_IMAGE_FILENAMES.get(category_name)
    if legacy_relative_path:
        legacy_absolute_path = os.path.join(app.static_folder, legacy_relative_path)
        if os.path.exists(legacy_absolute_path):
            return url_for("static", filename=legacy_relative_path)

    fallback_image = CATEGORY_DETAILS.get(category_name, {}).get("image_url")
    return resolve_image_url(fallback_image)


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def get_product_by_id(products, product_id):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def parse_product_form(form_data):
    category = form_data.get("category", "").strip()
    price_raw = form_data.get("price", "0").strip()

    try:
        price = int(price_raw)
    except ValueError:
        price = 0

    return {
        "name": form_data.get("name", "").strip(),
        "category": category,
        "price": price,
        "unit": form_data.get("unit", "").strip(),
        "addons": form_data.get("addons", "").strip(),
        "image": form_data.get("image", "").strip(),
    }


def validate_product_form(product_data):
    required_fields = ["name", "category", "unit"]
    missing_fields = [field for field in required_fields if not product_data[field]]

    if missing_fields:
        return False, "Please fill in name, category, unit, and price."

    if product_data["price"] <= 0:
        return False, "Price must be greater than zero."

    return True, ""

@app.route("/")
def index():
    products = load_products()

    grouped_products = {category: [] for category in CATEGORY_ORDER}

    for product in products:
        apply_product_image(product)

        category = product["category"]
        grouped_products.setdefault(category, []).append(product)

    categories = []

    for category in CATEGORY_ORDER:
        items = grouped_products.get(category, [])

        if not items:
            continue

        categories.append(
            {
                "name": category,
                "slug": slugify(category),
                "desc": CATEGORY_DETAILS.get(category, {}).get(
                    "desc",
                    "Browse products from this category.",
                ),
                "theme": CATEGORY_DETAILS.get(category, {}).get(
                    "theme",
                    "default",
                ),
                "image_url": get_category_image_url(category),
                "image_position": CATEGORY_DETAILS.get(category, {}).get(
                    "image_position",
                    "center",
                ),
                "image_size": CATEGORY_DETAILS.get(category, {}).get(
                    "image_size",
                    "cover",
                ),
                "items": items,
            }
        )

    return render_template(
        "index.html",
        categories=categories,
        hero_promos=build_hero_promos(products),
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))

        flash("Wrong password. Please try again.", "error")

    return render_template("admin_login.html")


@app.route("/addmin")
def addmin_dashboard_alias():
    return redirect(url_for("admin_dashboard"))


@app.route("/addmin/login", methods=["GET", "POST"])
def addmin_login_alias():
    return redirect(url_for("admin_login"), code=307 if request.method == "POST" else 302)


@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    products = load_products()
    products.sort(key=lambda item: (CATEGORY_ORDER.index(item["category"]) if item["category"] in CATEGORY_ORDER else 999, item["name"]))
    return render_template(
        "admin_dashboard.html",
        products=products,
        category_order=CATEGORY_ORDER,
    )


@app.route("/admin/products/add", methods=["POST"])
@admin_required
def admin_add_product():
    products = load_products()
    product_data = parse_product_form(request.form)
    is_valid, error_message = validate_product_form(product_data)

    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("admin_dashboard"))

    next_id = max((product["id"] for product in products), default=0) + 1
    product_data["id"] = next_id

    if not product_data["addons"]:
        product_data.pop("addons")

    if not product_data["image"]:
        product_data.pop("image")

    products.append(product_data)
    save_products(products)
    flash("Product added successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/products/<int:product_id>/edit", methods=["POST"])
@admin_required
def admin_edit_product(product_id):
    products = load_products()
    product = get_product_by_id(products, product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("admin_dashboard"))

    product_data = parse_product_form(request.form)
    is_valid, error_message = validate_product_form(product_data)

    if not is_valid:
        flash(error_message, "error")
        return redirect(url_for("admin_dashboard"))

    product.update(product_data)

    if not product["addons"]:
        product.pop("addons", None)

    if not product["image"]:
        product.pop("image", None)

    save_products(products)
    flash(f"{product['name']} updated.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def admin_delete_product(product_id):
    products = load_products()
    product = get_product_by_id(products, product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("admin_dashboard"))

    updated_products = [item for item in products if item["id"] != product_id]
    save_products(updated_products)
    flash(f"{product['name']} removed.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
