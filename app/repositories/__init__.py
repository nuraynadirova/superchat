"""
Factory: picks which repository implementation to use, based on settings.
In Phase 2 add e.g. `if settings.flight_source == "api": return TravelpayoutsFlightRepository(...)`.
"""
from ..config import settings
from .base import (CinemaRepository, DataSourceError, FlightRepository,
                   ProductRepository)
from .json_repo import (JsonCinemaRepository, JsonFlightRepository,
                        JsonProductRepository)


def make_flight_repo() -> FlightRepository:
    if settings.flight_source == "json":
        return JsonFlightRepository(settings.data_dir)
    raise ValueError(f"Unknown FLIGHT_SOURCE: {settings.flight_source}")


def make_product_repo() -> ProductRepository:
    if settings.product_source == "json":
        return JsonProductRepository(settings.data_dir)
    raise ValueError(f"Unknown PRODUCT_SOURCE: {settings.product_source}")


def make_cinema_repo() -> CinemaRepository:
    if settings.cinema_source == "json":
        return JsonCinemaRepository(settings.data_dir)
    raise ValueError(f"Unknown CINEMA_SOURCE: {settings.cinema_source}")


__all__ = ["DataSourceError", "make_flight_repo", "make_product_repo", "make_cinema_repo"]
