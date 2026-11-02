"""
Data-layer interfaces.

The rest of the application talks ONLY to these abstract classes.
Phase 1 uses JSON implementations (json_repo.py). In Phase 2 a real API
implementation (e.g. TravelpayoutsFlightRepository) is added that returns
records in the same shape, and nothing else in the app has to change.

Record shape = the field names of the official mock dataset (Appendix A).
Fields a real API cannot provide may be None.
"""
from abc import ABC, abstractmethod


class DataSourceError(Exception):
    """Raised when a data source fails (file missing, API down, timeout...)."""


class FlightRepository(ABC):
    @abstractmethod
    def search(self, origin: str | None = None, destination: str | None = None,
               date: str | None = None) -> list[dict]:
        """Return flights matching origin/destination city (or IATA code) and ISO date."""

    @abstractmethod
    def get(self, flight_id: str) -> dict | None: ...

    @abstractmethod
    def reserve(self, flight_id: str, passengers: int) -> dict:
        """Mock reservation. Returns a reservation dict or raises ValueError."""


class ProductRepository(ABC):
    @abstractmethod
    def all(self) -> list[dict]: ...

    @abstractmethod
    def get(self, product_id: str) -> dict | None: ...


class CinemaRepository(ABC):
    @abstractmethod
    def movies(self) -> list[dict]: ...

    @abstractmethod
    def movie(self, movie_id: str) -> dict | None: ...

    @abstractmethod
    def cinemas(self) -> list[dict]: ...

    @abstractmethod
    def cinema(self, cinema_id: str) -> dict | None: ...

    @abstractmethod
    def showtimes(self) -> list[dict]: ...

    @abstractmethod
    def showtime(self, showtime_id: str) -> dict | None: ...

    @abstractmethod
    def reserve(self, showtime_id: str, seats: int) -> dict:
        """Mock ticket reservation. Returns a reservation dict or raises ValueError."""
