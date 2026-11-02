"""
Offline tests of the data layer and tools (no LLM, no internet).
Run:  python -m pytest -q
They check the brief's sample scenarios at the data level.
"""
import pytest

from app.agent import Context
from app.config import settings
from app.repositories.json_repo import (JsonCinemaRepository,
                                        JsonFlightRepository,
                                        JsonProductRepository)
from app.state import SessionState
from app.tools import run_tool


@pytest.fixture
def ctx():
    d = settings.data_dir
    return Context(SessionState(), JsonFlightRepository(d), JsonProductRepository(d),
                   JsonCinemaRepository(d))


# ---------------- flights
def test_friday_baku_istanbul(ctx):
    r = run_tool(ctx, "search_flights", {"origin": "Baku", "destination": "Istanbul", "date": "2026-11-06"})
    assert [f["id"] for f in r["results"]] == ["F013", "F002", "F001"]  # sorted by price
    assert ctx.session.flights.last_results == ["F013", "F002", "F001"]


def test_cheaper_one_is_not_direct(ctx):
    r = run_tool(ctx, "search_flights", {"destination": "Istanbul", "date": "2026-11-06"})
    cheapest = r["results"][0]
    assert cheapest["id"] == "F013" and cheapest["stops"] == 1


def test_city_aliases(ctx):
    r1 = run_tool(ctx, "search_flights", {"origin": "Bakı", "destination": "Стамбул", "date": "2026-11-06"})
    r2 = run_tool(ctx, "search_flights", {"origin": "GYD", "destination": "IST", "date": "2026-11-06"})
    assert r1["count"] == r2["count"] == 3


def test_direct_only_filter(ctx):
    r = run_tool(ctx, "search_flights", {"destination": "Istanbul", "date": "2026-11-06", "max_stops": 0})
    assert all(f["stops"] == 0 for f in r["results"])


def test_no_flights_found(ctx):
    r = run_tool(ctx, "search_flights", {"origin": "Baku", "destination": "Paris"})
    assert r["results"] == [] and "note" in r


def test_reserve_flight_and_seat_limit(ctx):
    r = run_tool(ctx, "reserve_flight", {"flight_id": "F002", "passengers": 2})
    assert r["total_azn"] == 490.0
    r = run_tool(ctx, "reserve_flight", {"flight_id": "F002", "passengers": 5})
    assert "error" in r  # only 1 seat left now


def test_compare_flights(ctx):
    r = run_tool(ctx, "compare_flights", {"flight_ids": ["F001", "F002"]})
    assert r["cheapest"] == "F002" and r["most_baggage"] == "F001"


# ---------------- shopping
def test_headphones_under_100(ctx):
    r = run_tool(ctx, "search_products", {"query": "wireless headphones", "max_price": 100})
    assert [p["id"] for p in r["results"]] == ["P001"]


def test_laptops_second_in_stock(ctx):
    r = run_tool(ctx, "search_products", {"query": "laptops"})
    ids = [p["id"] for p in r["results"]]
    assert set(ids) == {"P003", "P004"}
    second = r["results"][1]
    assert second["stock"] > 0


def test_backpack(ctx):
    r = run_tool(ctx, "search_products", {"query": "backpack"})
    assert [p["id"] for p in r["results"]] == ["P010"]


def test_out_of_stock_cannot_be_added(ctx):
    r = run_tool(ctx, "add_to_cart", {"product_id": "P002"})
    assert "error" in r


def test_cart_total(ctx):
    run_tool(ctx, "add_to_cart", {"product_id": "P001", "quantity": 2})
    run_tool(ctx, "add_to_cart", {"product_id": "P010"})
    r = run_tool(ctx, "view_cart", {})
    assert r["total_azn"] == round(89.9 * 2 + 65.0, 2)
    r = run_tool(ctx, "remove_from_cart", {"product_id": "P001", "quantity": 1})
    assert r["cart"]["total_azn"] == round(89.9 + 65.0, 2)


def test_localised_names(ctx):
    ctx.session.language = "az"
    r = run_tool(ctx, "search_products", {"query": "laptop"})
    assert r["results"][0]["name"].startswith("Noutbuk")


# ---------------- cinema
def test_tonight(ctx):
    r = run_tool(ctx, "get_showtimes", {"date": "2026-11-02", "time_from": "17:00"})
    assert [s["id"] for s in r["results"]] == ["S001", "S003", "S002"]
    sold_out = [s for s in r["results"] if s["status"] == "SOLD OUT"]
    assert [s["movie"] for s in sold_out] == ["Deep Signal"]


def test_scifi_saturday_has_two_candidates(ctx):
    r = run_tool(ctx, "search_movies", {"genre": "sci-fi", "date": "2026-11-07"})
    assert {m["title"] for m in r["results"]} == {"Orbit Zero", "Deep Signal"}


def test_reserve_tickets(ctx):
    r = run_tool(ctx, "reserve_tickets", {"showtime_id": "S012", "seats": 2})
    assert r["total_azn"] == 28.0 and r["showtime"]["seats_available"] == 3
    r = run_tool(ctx, "reserve_tickets", {"showtime_id": "S003", "seats": 1})
    assert "error" in r  # sold out


# ---------------- robustness
def test_bad_arguments_do_not_crash(ctx):
    r = run_tool(ctx, "search_flights", {"nonsense": 1})
    assert "error" in r
    r = run_tool(ctx, "no_such_tool", {})
    assert "error" in r


def test_state_kept_per_domain(ctx):
    run_tool(ctx, "search_products", {"query": "headphones"})
    run_tool(ctx, "search_flights", {"destination": "Dubai"})
    run_tool(ctx, "search_movies", {"genre": "comedy"})
    assert ctx.session.shopping.last_results == ["P001"]  # still intact
