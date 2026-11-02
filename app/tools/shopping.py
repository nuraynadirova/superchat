"""Shopping module: search/filter, details, compare, stock, cart."""
import re

# Words that point to a category even if they are not in the product name
CATEGORY_SYNONYMS = {
    "computers": ["laptop", "notebook", "computer", "pc"],
    "phones": ["phone", "smartphone", "mobile"],
    "audio": ["headphone", "earbud", "earphone", "speaker", "audio", "sound"],
    "wearables": ["watch", "smartwatch", "wearable"],
    "sport": ["shoe", "sneaker", "running", "sport"],
    "accessories": ["backpack", "bag", "accessory"],
    "home": ["coffee", "kitchen", "home"],
    "gifts": ["gift", "game", "board"],
}

STOP_WORDS = {"the", "a", "an", "for", "with", "and", "or", "of", "me", "show", "some", "any", "under"}


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[\w\"]+", text.lower())
    out = []
    for w in words:
        if w in STOP_WORDS or len(w) < 2:
            continue
        # crude singularisation: laptops -> laptop, headphones -> headphone
        if len(w) > 4 and w.endswith("es") and not w.endswith("ses"):
            w = w[:-1] if w.endswith("nes") else w[:-2]
        elif len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        out.append(w)
    return out


def _haystack(p: dict) -> list[tuple[list[str], int]]:
    """Word groups with weights: name/brand/category/colour > category synonyms > description."""
    main = _tokens(" ".join([*p["name"].values(), p["category"], p["brand"], p["color"]]))
    return [(main, 3), (CATEGORY_SYNONYMS.get(p["category"], []), 2),
            (_tokens(p.get("description", "")), 1)]


def _match(q: str, words: list[str]) -> bool:
    return any(h.startswith(q) or (len(h) >= 4 and q.startswith(h)) for h in words)


def _score(query_tokens: list[str], hay: list[tuple[list[str], int]]) -> int:
    """Each query word scores the weight of the best group it matches."""
    return sum(max((w for words, w in hay if _match(q, words)), default=0) for q in query_tokens)


def _short(p: dict, lang: str = "en", idx: int | None = None) -> dict:
    d = {
        "id": p["id"], "name": p["name"].get(lang, p["name"]["en"]), "category": p["category"],
        "brand": p["brand"], "price_azn": p["price_azn"], "rating": p["rating"],
        "color": p["color"], "stock": p["stock"],
        "availability": "in stock" if p["stock"] > 0 else "OUT OF STOCK",
    }
    if idx is not None:
        d = {"position": idx, **d}
    return d


def search_products(ctx, query=None, category=None, brand=None, min_price=None,
                    max_price=None, color=None, in_stock_only=False, sort_by="relevance"):
    products = list(ctx.product_repo.all())
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    if brand:
        products = [p for p in products if p["brand"].lower() == brand.lower()]
    if color:
        products = [p for p in products if p["color"].lower() == color.lower()]
    if min_price is not None:
        products = [p for p in products if p["price_azn"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price_azn"] <= max_price]
    if in_stock_only:
        products = [p for p in products if p["stock"] > 0]

    if query:
        qt = _tokens(query)
        scored = [(p, _score(qt, _haystack(p))) for p in products]
        best = max((s for _, s in scored), default=0)
        products = [p for p, s in scored if s > 0 and s == best]

    if sort_by == "price_asc":
        products.sort(key=lambda p: p["price_azn"])
    elif sort_by == "price_desc":
        products.sort(key=lambda p: -p["price_azn"])
    elif sort_by == "rating":
        products.sort(key=lambda p: -p["rating"])

    st = ctx.session.shopping
    st.last_query = {k: v for k, v in dict(query=query, category=category, brand=brand,
                     min_price=min_price, max_price=max_price, color=color).items() if v is not None}
    st.last_results = [p["id"] for p in products]
    if not products:
        return {"results": [], "note": "No products in the catalogue match these criteria.",
                "available_categories": sorted({p["category"] for p in ctx.product_repo.all()})}
    lang = ctx.session.language
    return {"count": len(products),
            "results": [_short(p, lang, i + 1) for i, p in enumerate(products)]}


def get_product_details(ctx, product_id):
    p = ctx.product_repo.get(product_id)
    if not p:
        return {"error": f"Product {product_id} not found."}
    ctx.session.shopping.selected = p["id"]
    return {**_short(p, ctx.session.language), "description": p.get("description"),
            "names": p["name"]}


def compare_products(ctx, product_ids):
    items = [ctx.product_repo.get(i) for i in product_ids]
    missing = [i for i, p in zip(product_ids, items) if p is None]
    items = [p for p in items if p]
    if len(items) < 2:
        return {"error": "Need at least two existing products to compare.", "missing": missing}
    lang = ctx.session.language
    return {"products": [{**_short(p, lang), "description": p.get("description")} for p in items],
            "cheapest": min(items, key=lambda p: p["price_azn"])["id"],
            "best_rated": max(items, key=lambda p: p["rating"])["id"],
            "missing": missing}


def _cart_view(ctx):
    lines, total = [], 0.0
    for pid, qty in ctx.session.shopping.cart.items():
        p = ctx.product_repo.get(pid)
        if not p:
            continue
        subtotal = round(p["price_azn"] * qty, 2)
        total += subtotal
        lines.append({"id": pid, "name": p["name"].get(ctx.session.language, p["name"]["en"]),
                      "quantity": qty, "unit_price_azn": p["price_azn"], "subtotal_azn": subtotal})
    return {"items": lines, "total_azn": round(total, 2)}


def add_to_cart(ctx, product_id, quantity=1):
    p = ctx.product_repo.get(product_id)
    if not p:
        return {"error": f"Product {product_id} not found."}
    cart = ctx.session.shopping.cart
    wanted = cart.get(p["id"], 0) + int(quantity)
    if p["stock"] < wanted:
        return {"error": f"Only {p['stock']} in stock, cannot add {quantity}.", "stock": p["stock"]}
    cart[p["id"]] = wanted
    ctx.session.shopping.selected = p["id"]
    return {"added": p["id"], "quantity": int(quantity), "cart": _cart_view(ctx)}


def remove_from_cart(ctx, product_id, quantity=None):
    cart = ctx.session.shopping.cart
    pid = product_id.upper()
    if pid not in cart:
        return {"error": f"{product_id} is not in the cart.", "cart": _cart_view(ctx)}
    if quantity is None or int(quantity) >= cart[pid]:
        del cart[pid]
    else:
        cart[pid] -= int(quantity)
    return {"removed": pid, "cart": _cart_view(ctx)}


def view_cart(ctx):
    return _cart_view(ctx)


FUNCTIONS = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "compare_products": compare_products,
    "add_to_cart": add_to_cart,
    "remove_from_cart": remove_from_cart,
    "view_cart": view_cart,
}

SCHEMAS = [
    {"type": "function", "function": {
        "name": "search_products",
        "description": "Search the product catalogue. `query` should be short English keywords "
                       "(e.g. 'wireless headphones', 'laptop'). Categories: audio, computers, phones, "
                       "wearables, sport, accessories, home, gifts. All parameters optional.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"},
            "category": {"type": "string"},
            "brand": {"type": "string"},
            "min_price": {"type": "number"},
            "max_price": {"type": "number"},
            "color": {"type": "string", "description": "English colour name, e.g. black"},
            "in_stock_only": {"type": "boolean"},
            "sort_by": {"type": "string", "enum": ["relevance", "price_asc", "price_desc", "rating"]},
        }}}},
    {"type": "function", "function": {
        "name": "get_product_details",
        "description": "Details and stock of one product.",
        "parameters": {"type": "object", "properties": {"product_id": {"type": "string"}},
                       "required": ["product_id"]}}},
    {"type": "function", "function": {
        "name": "compare_products",
        "description": "Compare two or more products.",
        "parameters": {"type": "object", "properties": {
            "product_ids": {"type": "array", "items": {"type": "string"}}},
            "required": ["product_ids"]}}},
    {"type": "function", "function": {
        "name": "add_to_cart",
        "description": "Add a product to the cart (checks stock).",
        "parameters": {"type": "object", "properties": {
            "product_id": {"type": "string"}, "quantity": {"type": "integer", "minimum": 1}},
            "required": ["product_id"]}}},
    {"type": "function", "function": {
        "name": "remove_from_cart",
        "description": "Remove a product (or some quantity of it) from the cart.",
        "parameters": {"type": "object", "properties": {
            "product_id": {"type": "string"}, "quantity": {"type": "integer", "minimum": 1}},
            "required": ["product_id"]}}},
    {"type": "function", "function": {
        "name": "view_cart",
        "description": "Show the cart contents and total.",
        "parameters": {"type": "object", "properties": {}}}},
]
