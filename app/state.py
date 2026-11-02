"""
Conversation state.

- One SessionState per chat session (shared: language, preferences, last domain).
- Inside it, one separate state object per domain. Switching domain never
  clears another domain's state, so "back to the headphones" works.
"""
from dataclasses import dataclass, field


@dataclass
class FlightState:
    last_query: dict = field(default_factory=dict)       # e.g. {"destination": "Istanbul", "date": "2026-11-06"}
    last_results: list[str] = field(default_factory=list)  # flight ids in the order shown to the user
    selected: str | None = None
    reservations: list[dict] = field(default_factory=list)


@dataclass
class ShoppingState:
    last_query: dict = field(default_factory=dict)
    last_results: list[str] = field(default_factory=list)  # product ids in shown order
    selected: str | None = None
    cart: dict[str, int] = field(default_factory=dict)     # product_id -> quantity


@dataclass
class CinemaState:
    last_query: dict = field(default_factory=dict)
    last_movies: list[str] = field(default_factory=list)     # movie ids in shown order
    last_showtimes: list[str] = field(default_factory=list)  # showtime ids in shown order
    selected_movie: str | None = None
    selected_showtime: str | None = None
    reservations: list[dict] = field(default_factory=list)


@dataclass
class SessionState:
    language: str = "en"
    last_domain: str | None = None
    preferences: list[str] = field(default_factory=list)
    flights: FlightState = field(default_factory=FlightState)
    shopping: ShoppingState = field(default_factory=ShoppingState)
    cinema: CinemaState = field(default_factory=CinemaState)
    history: list[dict] = field(default_factory=list)  # [{"role": "user"/"assistant", "content": ..., "domain": ...}]

    def summary(self) -> str:
        """Short text summary of the state, given to the LLM on every turn."""
        f, s, c = self.flights, self.shopping, self.cinema
        lines = [
            f"Last active domain: {self.last_domain or 'none'}",
            f"User language: {self.language}",
        ]
        if self.preferences:
            lines.append("Stated preferences: " + "; ".join(self.preferences))
        lines.append(f"FLIGHTS: last search={f.last_query or '-'}; "
                     f"results shown in order={f.last_results or '-'}; selected={f.selected or '-'}; "
                     f"reservations={[r['reservation_id'] for r in f.reservations] or '-'}")
        lines.append(f"SHOPPING: last search={s.last_query or '-'}; "
                     f"results shown in order={s.last_results or '-'}; selected={s.selected or '-'}; "
                     f"cart={s.cart or 'empty'}")
        lines.append(f"CINEMA: last search={c.last_query or '-'}; "
                     f"movies shown in order={c.last_movies or '-'}; "
                     f"showtimes shown in order={c.last_showtimes or '-'}; "
                     f"selected movie={c.selected_movie or '-'}; selected showtime={c.selected_showtime or '-'}; "
                     f"reservations={[r['reservation_id'] for r in c.reservations] or '-'}")
        return "\n".join(lines)


# In-memory store of sessions (enough for Phase 1 / demo).
_SESSIONS: dict[str, SessionState] = {}


def get_session(session_id: str) -> SessionState:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = SessionState()
    return _SESSIONS[session_id]


def reset_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)
