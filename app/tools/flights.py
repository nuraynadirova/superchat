"""Flights module: search, filter/sort, details, compare, mock reservation."""


def _short(f: dict, idx: int | None = None) -> dict:
    d = {
        "id": f["id"], "airline": f["airline"], "flight_number": f["flight_number"],
        "from": f"{f['origin']['city']} ({f['origin']['code']})",
        "to": f"{f['destination']['city']} ({f['destination']['code']})",
        "departure": f["departure_local"], "arrival": f["arrival_local"],
        "duration_min": f["duration_min"], "stops": f["stops"], "via": f["via"],
        "price_azn": f["price_azn"], "cabin": f["cabin"],
        "baggage_kg": f.get("baggage_kg"), "seats_available": f.get("seats_available"),
    }
    if idx is not None:
        d = {"position": idx, **d}
    return d


def search_flights(ctx, origin=None, destination=None, date=None, date_to=None,
                   max_stops=None, airline=None, cabin=None, max_price=None,
                   depart_after=None, depart_before=None, sort_by="price"):
    if date and date_to:
        # date range: query without date, then filter
        flights = [f for f in ctx.flight_repo.search(origin, destination, None)
                   if date <= f["departure_local"][:10] <= date_to]
    else:
        flights = ctx.flight_repo.search(origin, destination, date)

    if max_stops is not None:
        flights = [f for f in flights if f["stops"] <= max_stops]
    if airline:
        flights = [f for f in flights if airline.lower() in f["airline"].lower()]
    if cabin:
        flights = [f for f in flights if f["cabin"].lower() == cabin.lower()]
    if max_price is not None:
        flights = [f for f in flights if f["price_azn"] <= max_price]
    if depart_after:
        flights = [f for f in flights if f["departure_local"][11:16] >= depart_after]
    if depart_before:
        flights = [f for f in flights if f["departure_local"][11:16] <= depart_before]

    keys = {
        "price": lambda f: f["price_azn"],
        "departure": lambda f: f["departure_local"],
        "duration": lambda f: f["duration_min"],
        "stops": lambda f: (f["stops"], f["price_azn"]),
    }
    flights.sort(key=keys.get(sort_by, keys["price"]))

    st = ctx.session.flights
    st.last_query = {k: v for k, v in dict(origin=origin, destination=destination, date=date,
                     date_to=date_to, max_stops=max_stops, airline=airline, cabin=cabin,
                     max_price=max_price, sort_by=sort_by).items() if v is not None}
    st.last_results = [f["id"] for f in flights]
    if not flights:
        return {"results": [], "note": "No flights in the data match these criteria."}
    return {"count": len(flights), "sorted_by": sort_by,
            "results": [_short(f, i + 1) for i, f in enumerate(flights)]}


def get_flight_details(ctx, flight_id):
    f = ctx.flight_repo.get(flight_id)
    if not f:
        return {"error": f"Flight {flight_id} not found."}
    ctx.session.flights.selected = f["id"]
    return _short(f)


def compare_flights(ctx, flight_ids):
    flights = [ctx.flight_repo.get(i) for i in flight_ids]
    missing = [i for i, f in zip(flight_ids, flights) if f is None]
    flights = [f for f in flights if f]
    if len(flights) < 2:
        return {"error": "Need at least two existing flights to compare.", "missing": missing}
    return {
        "flights": [_short(f) for f in flights],
        "cheapest": min(flights, key=lambda f: f["price_azn"])["id"],
        "shortest": min(flights, key=lambda f: f["duration_min"])["id"],
        "most_baggage": max(flights, key=lambda f: f.get("baggage_kg") or 0)["id"],
        "missing": missing,
    }


def reserve_flight(ctx, flight_id, passengers=1):
    try:
        r = ctx.flight_repo.reserve(flight_id, int(passengers))
    except ValueError as e:
        return {"error": str(e)}
    ctx.session.flights.selected = r["flight_id"]
    ctx.session.flights.reservations.append(r)
    return r


FUNCTIONS = {
    "search_flights": search_flights,
    "get_flight_details": get_flight_details,
    "compare_flights": compare_flights,
    "reserve_flight": reserve_flight,
}

SCHEMAS = [
    {"type": "function", "function": {
        "name": "search_flights",
        "description": "Search flights in the catalogue. Cities may be names or IATA codes "
                       "(English names preferred, e.g. Baku, Istanbul). All parameters optional.",
        "parameters": {"type": "object", "properties": {
            "origin": {"type": "string"},
            "destination": {"type": "string"},
            "date": {"type": "string", "description": "Departure date YYYY-MM-DD (or start of range)"},
            "date_to": {"type": "string", "description": "End of a date range YYYY-MM-DD"},
            "max_stops": {"type": "integer", "description": "0 = direct only"},
            "airline": {"type": "string"},
            "cabin": {"type": "string", "enum": ["economy", "business"]},
            "max_price": {"type": "number", "description": "AZN"},
            "depart_after": {"type": "string", "description": "HH:MM"},
            "depart_before": {"type": "string", "description": "HH:MM"},
            "sort_by": {"type": "string", "enum": ["price", "departure", "duration", "stops"]},
        }}}},
    {"type": "function", "function": {
        "name": "get_flight_details",
        "description": "Full details of one flight (times, duration, stops, baggage, seats left).",
        "parameters": {"type": "object", "properties": {"flight_id": {"type": "string"}},
                       "required": ["flight_id"]}}},
    {"type": "function", "function": {
        "name": "compare_flights",
        "description": "Compare two or more flights side by side.",
        "parameters": {"type": "object", "properties": {
            "flight_ids": {"type": "array", "items": {"type": "string"}}},
            "required": ["flight_ids"]}}},
    {"type": "function", "function": {
        "name": "reserve_flight",
        "description": "Make a MOCK reservation (no payment). Only call when the user clearly "
                       "asked to book/reserve a specific flight.",
        "parameters": {"type": "object", "properties": {
            "flight_id": {"type": "string"},
            "passengers": {"type": "integer", "minimum": 1}},
            "required": ["flight_id", "passengers"]}}},
]
