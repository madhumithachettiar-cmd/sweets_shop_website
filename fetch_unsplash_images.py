import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


APP_DIR = Path(__file__).resolve().parent
PRODUCTS_PATH = APP_DIR / "products.json"
UTM_SOURCE = "sandesh_sweets"
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

QUERY_OVERRIDES = {
    "Kaju Katali": "kaju katli indian sweet",
    "Kaju Kesar Katali": "kaju kesar katli indian sweet",
    "Mix Kaju Katali": "mixed kaju katli indian sweet",
    "Kaju Anjeer Katali": "kaju anjeer katli indian sweet",
    "Dry Frit Apple": "dry fruit apple mithai",
    "Dry Fruit Water Melon": "watermelon shaped indian sweet",
    "Angeer Dry Fruit Vati": "anjeer dry fruit mithai",
    "Dry-Frit Diamond Cake": "dry fruit diamond sweet",
    "Dry Fruit Chandra Kala": "chandra kala sweet",
    "Mix Dry Fruit Sweets": "mixed dry fruit mithai",
    "Angeer Malai Barfi": "anjeer malai barfi",
    "Malai Milk Cake": "milk cake indian sweet",
    "Chocolate Mawa Barfi": "chocolate mawa barfi",
    "Chocolate Mawa Roll": "chocolate mawa roll sweet",
    "Pista Mawa Roll": "pista mawa roll sweet",
    "Malai Pedha (Regular Size)": "malai pedha indian sweet",
    "Malai Pedha (Small Size)": "malai pedha indian sweet",
    "Malai Pedha White": "white peda indian sweet",
    "Mawa Pedha (Regular Size)": "mawa pedha indian sweet",
    "Mawa Pedha (Small Size)": "mawa pedha indian sweet",
    "Kandi Pedha": "kandi peda indian sweet",
    "Laddu": "ladoo indian sweet",
    "Besan Laddu": "besan ladoo",
    "Laddu Pure Ghee": "ghee ladoo",
    "Dink Laddu": "dink ladoo",
    "Mumbai Halwai": "bombay halwa indian sweet",
    "Mysore Pak": "mysore pak",
    "Mumbai Halwa (Ghee)": "bombay halwa indian sweet",
    "Pinapple Halwa (Ghee)": "pineapple halwa indian sweet",
    "Maharaja Halwa (Ghee)": "indian halwa sweet",
    "Badam Halwa": "badam halwa",
    "Angeer Halwa": "anjeer halwa",
    "Sonpapdi": "soan papdi indian sweet",
    "Balushahi": "balushahi indian sweet",
    "Batisa": "batisa indian sweet",
    "Jilabi": "jalebi indian sweet",
}


def load_products():
    with PRODUCTS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_products(products):
    with PRODUCTS_PATH.open("w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)
        file.write("\n")


def build_query(product):
    if product["name"] in QUERY_OVERRIDES:
        return QUERY_OVERRIDES[product["name"]]

    return f"{product['name']} {product['category']} indian sweet"


def unsplash_request(url):
    request = Request(
        url,
        headers={
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}",
            "Accept-Version": "v1",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_result(photo):
    photographer_link = (
        f"{photo['user']['links']['html']}"
        f"?utm_source={UTM_SOURCE}&utm_medium=referral"
    )

    return {
        "unsplash_photo_id": photo["id"],
        "image_url": photo["urls"]["regular"],
        "image_thumb_url": photo["urls"]["small"],
        "image_alt": photo.get("alt_description") or "Sweet product photo",
        "photographer_name": photo["user"]["name"],
        "photographer_link": photographer_link,
    }


def fetch_image_for_product(product, used_photo_ids):
    query = quote_plus(build_query(product))
    url = (
        "https://api.unsplash.com/search/photos"
        f"?query={query}&page=1&per_page=8&orientation=landscape&content_filter=high"
    )

    data = unsplash_request(url)
    results = data.get("results", [])

    if not results:
        return None

    selected = None

    for photo in results:
        if photo["id"] not in used_photo_ids:
            selected = photo
            break

    if selected is None:
        selected = results[0]

    used_photo_ids.add(selected["id"])
    return normalize_result(selected)


def clear_existing_image_fields(product):
    for field in [
        "unsplash_photo_id",
        "image_url",
        "image_thumb_url",
        "image_alt",
        "photographer_name",
        "photographer_link",
    ]:
        product.pop(field, None)


def main():
    if not UNSPLASH_ACCESS_KEY:
        print("UNSPLASH_ACCESS_KEY is not set.", file=sys.stderr)
        return 1

    products = load_products()
    used_photo_ids = set()
    updated_count = 0
    failed_count = 0
    no_result_count = 0

    existing_ids = {
        product.get("unsplash_photo_id")
        for product in products
        if product.get("unsplash_photo_id")
    }
    used_photo_ids.update(existing_ids)

    for index, product in enumerate(products, start=1):
        print(f"[{index}/{len(products)}] Fetching image for {product['name']}...")
        try:
            image_data = fetch_image_for_product(product, used_photo_ids)
        except HTTPError as error:
            failed_count += 1
            error_body = ""
            try:
                error_body = error.read().decode("utf-8")
            except Exception:
                error_body = "<unable to read response body>"
            print(
                f"HTTP error for {product['name']}: {error.code} {error.reason} {error_body}",
                file=sys.stderr,
            )
            continue
        except (URLError, TimeoutError) as error:
            failed_count += 1
            print(f"Failed for {product['name']}: {error}", file=sys.stderr)
            continue

        clear_existing_image_fields(product)

        if image_data:
            product.update(image_data)
            updated_count += 1
        else:
            no_result_count += 1
            print(f"No Unsplash results for {product['name']}")

        time.sleep(1)

    save_products(products)
    print("Saved image metadata to products.json")
    print(
        f"Summary: updated={updated_count}, no_results={no_result_count}, failed={failed_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
