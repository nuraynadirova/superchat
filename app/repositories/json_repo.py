"""
Phase 1: repositories that read the official mock JSON files.

Data is loaded once into memory. Reservations decrease seat counts in memory
only (the JSON files on disk are never modified).
"""
import copy
import json
import uuid
from pathlib import Path

from .base import (CinemaRepository, DataSourceError, FlightRepository,
                   ProductRepository)

# City name variants (en / az / ru) -> IATA code used in flights.json
CITY_ALIASES = {
    "GYD": ["baku", "bakı", "baki", "баку"],
    "IST": ["istanbul", "i̇stanbul", "стамбул", "истанбул"],
    "DXB": ["dubai", "dubay", "дубай"],
    "SVO": ["moscow", "moskva", "москва"],
    "TBS": ["tbilisi", "tiflis", "тбилиси"],
    "TAS": ["tashkent", "daşkənd", "dashkent", "ташкент"],
}


def _load(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise DataSourceError(f"Cannot read {path.name}") from e


def _city_matches(query: str, place: dict) -> bool:
    """True if the user's city text matches a flight's origin/destination."""
    q = query.strip().lower()
    if q in (place["code"].lower(), place["city"].lower()):
        return True
    return q in CITY_ALIASES.get(place["code"], [])


class JsonFlightRepository(FlightRepository):
    def __init__(self, data_dir: Path):
        self._flights = copy.deepcopy(_load(data_dir / "flights.json"))
        # Some codes in the data may differ from our alias table (e.g. Moscow airport);
        # register every code/city that actually appears in the file.
        for f in self._flights:
            for place in (f["origin"], f["destination"]):
                CITY_ALIASES.setdefault(place["code"], []).append(place["city"].lower())

    def search(self, origin=None, destination=None, date=None):
        result = []
        for f in self._flights:
            if origin and not _city_matches(origin, f["origin"]):
                continue
            if destination and not _city_matches(destination, f["destination"]):
                continue
            if date and not f["departure_local"].startswith(date):
                continue
            result.append(f)
        return result

    def get(self, flight_id):
        return next((f for f in self._flights if f["id"].upper() == flight_id.upper()), None)

    def reserve(self, flight_id, passengers):
        f = self.get(flight_id)
        if f is None:
            raise ValueError("flight_not_found")
        if passengers < 1:
            raise ValueError("invalid_passenger_count")
        if f["seats_available"] < passengers:
            raise ValueError(f"not_enough_seats (only {f['seats_available']} left)")
        f["seats_available"] -= passengers
        return {
            "reservation_id": "FR-" + uuid.uuid4().hex[:6].upper(),
            "flight_id": f["id"], "flight_number": f["flight_number"],
            "passengers": passengers,
            "total_azn": round(f["price_azn"] * passengers, 2),
            "status": "reserved (mock, no payment)",
        }


class JsonProductRepository(ProductRepository):
    def __init__(self, data_dir: Path):
        self._products = copy.deepcopy(_load(data_dir / "products.json"))

    def all(self):
        return self._products

    def get(self, product_id):
        return next((p for p in self._products if p["id"].upper() == product_id.upper()), None)


class JsonCinemaRepository(CinemaRepository):
    def __init__(self, data_dir: Path):
        self._movies = _load(data_dir / "movies.json")
        self._cinemas = _load(data_dir / "cinemas.json")
        self._showtimes = copy.deepcopy(_load(data_dir / "showtimes.json"))

    def movies(self):
        return self._movies

    def movie(self, movie_id):
        return next((m for m in self._movies if m["id"].upper() == movie_id.upper()), None)

    def cinemas(self):
        return self._cinemas

    def cinema(self, cinema_id):
        return next((c for c in self._cinemas if c["id"].upper() == cinema_id.upper()), None)

    def showtimes(self):
        return self._showtimes

    def showtime(self, showtime_id):
        return next((s for s in self._showtimes if s["id"].upper() == showtime_id.upper()), None)

    def reserve(self, showtime_id, seats):
        s = self.showtime(showtime_id)
        if s is None:
            raise ValueError("showtime_not_found")
        if seats < 1:
            raise ValueError("invalid_seat_count")
        if s["seats_available"] < seats:
            raise ValueError(f"not_enough_seats (only {s['seats_available']} left)")
        s["seats_available"] -= seats
        return {
            "reservation_id": "CR-" + uuid.uuid4().hex[:6].upper(),
            "showtime_id": s["id"], "seats": seats,
            "total_azn": round(s["price_azn"] * seats, 2),
            "status": "reserved (mock, no payment)",
        }
