"""Cinema module: films, cinemas, showtimes, seats, mock ticket reservation."""


def _movie_short(m: dict, idx: int | None = None) -> dict:
    d = {"id": m["id"], "title": m["title"], "genre": m["genre"], "language": m["language"],
         "duration_min": m["duration_min"], "age_rating": m["age_rating"], "rating": m["rating"]}
    if idx is not None:
        d = {"position": idx, **d}
    return d


def _showtime_view(ctx, s: dict, idx: int | None = None) -> dict:
    m = ctx.cinema_repo.movie(s["movie_id"]) or {}
    c = ctx.cinema_repo.cinema(s["cinema_id"]) or {}
    d = {"id": s["id"], "movie_id": s["movie_id"], "movie": m.get("title"),
         "cinema_id": s["cinema_id"], "cinema": c.get("name"), "district": c.get("district"),
         "date": s["date"], "time": s["time"], "hall": s["hall"], "price_azn": s["price_azn"],
         "seats_available": s["seats_available"], "seats_total": s["seats_total"],
         "status": "SOLD OUT" if s["seats_available"] == 0 else "available"}
    if idx is not None:
        d = {"position": idx, **d}
    return d


def search_movies(ctx, title=None, genre=None, language=None, min_rating=None, date=None):
    movies = list(ctx.cinema_repo.movies())
    if title:
        movies = [m for m in movies if title.lower() in m["title"].lower()]
    if genre:
        g = genre.lower().replace("scifi", "sci-fi").replace("science fiction", "sci-fi")
        movies = [m for m in movies if any(g in x.lower() for x in m["genre"])]
    if language:
        movies = [m for m in movies if m["language"].lower().startswith(language.lower()[:3])]
    if min_rating is not None:
        movies = [m for m in movies if m["rating"] >= min_rating]
    if date:
        showing = {s["movie_id"] for s in ctx.cinema_repo.showtimes() if s["date"] == date}
        movies = [m for m in movies if m["id"] in showing]
    movies.sort(key=lambda m: -m["rating"])

    st = ctx.session.cinema
    st.last_query = {k: v for k, v in dict(title=title, genre=genre, language=language,
                     min_rating=min_rating, date=date).items() if v is not None}
    st.last_movies = [m["id"] for m in movies]
    if not movies:
        return {"results": [], "note": "No films in the data match these criteria."}
    return {"count": len(movies), "results": [_movie_short(m, i + 1) for i, m in enumerate(movies)]}


def get_showtimes(ctx, movie_id=None, date=None, date_to=None, cinema_id=None,
                  time_from=None, time_to=None):
    shows = list(ctx.cinema_repo.showtimes())
    if movie_id:
        shows = [s for s in shows if s["movie_id"].upper() == movie_id.upper()]
    if date and date_to:
        shows = [s for s in shows if date <= s["date"] <= date_to]
    elif date:
        shows = [s for s in shows if s["date"] == date]
    if cinema_id:
        shows = [s for s in shows if s["cinema_id"].upper() == cinema_id.upper()]
    if time_from:
        shows = [s for s in shows if s["time"] >= time_from]
    if time_to:
        shows = [s for s in shows if s["time"] <= time_to]
    shows.sort(key=lambda s: (s["date"], s["time"]))

    st = ctx.session.cinema
    st.last_showtimes = [s["id"] for s in shows]
    if movie_id:
        st.selected_movie = movie_id.upper()
    if not shows:
        return {"results": [], "note": "No showtimes in the data match these criteria."}
    return {"count": len(shows), "results": [_showtime_view(ctx, s, i + 1) for i, s in enumerate(shows)]}


def get_movie_details(ctx, movie_id):
    m = ctx.cinema_repo.movie(movie_id)
    if not m:
        return {"error": f"Film {movie_id} not found."}
    ctx.session.cinema.selected_movie = m["id"]
    return {**_movie_short(m), "synopsis": m.get("synopsis")}


def get_showtime_details(ctx, showtime_id):
    s = ctx.cinema_repo.showtime(showtime_id)
    if not s:
        return {"error": f"Showtime {showtime_id} not found."}
    ctx.session.cinema.selected_showtime = s["id"]
    ctx.session.cinema.selected_movie = s["movie_id"]
    return _showtime_view(ctx, s)


def list_cinemas(ctx):
    return {"cinemas": ctx.cinema_repo.cinemas()}


def reserve_tickets(ctx, showtime_id, seats=1):
    try:
        r = ctx.cinema_repo.reserve(showtime_id, int(seats))
    except ValueError as e:
        return {"error": str(e)}
    st = ctx.session.cinema
    st.reservations.append(r)
    st.selected_showtime = r["showtime_id"]
    return {**r, "showtime": _showtime_view(ctx, ctx.cinema_repo.showtime(showtime_id))}


FUNCTIONS = {
    "search_movies": search_movies,
    "get_movie_details": get_movie_details,
    "get_showtimes": get_showtimes,
    "get_showtime_details": get_showtime_details,
    "list_cinemas": list_cinemas,
    "reserve_tickets": reserve_tickets,
}

SCHEMAS = [
    {"type": "function", "function": {
        "name": "search_movies",
        "description": "List films. Filter by title, genre (sci-fi, thriller, adventure, drama, comedy, "
                       "horror, mystery, animation, family, action, crime, romance), language "
                       "(English, Azerbaijani, Russian), minimum rating, or date (only films that have "
                       "a showtime on that date).",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"}, "genre": {"type": "string"},
            "language": {"type": "string"}, "min_rating": {"type": "number"},
            "date": {"type": "string", "description": "YYYY-MM-DD"}}}}},
    {"type": "function", "function": {
        "name": "get_movie_details",
        "description": "Details and synopsis of one film.",
        "parameters": {"type": "object", "properties": {"movie_id": {"type": "string"}},
                       "required": ["movie_id"]}}},
    {"type": "function", "function": {
        "name": "get_showtimes",
        "description": "Showtimes with cinema, hall, price and seats available. 'Tonight' = today's "
                       "date with time_from 17:00.",
        "parameters": {"type": "object", "properties": {
            "movie_id": {"type": "string"}, "date": {"type": "string", "description": "YYYY-MM-DD"},
            "date_to": {"type": "string", "description": "End of date range YYYY-MM-DD"},
            "cinema_id": {"type": "string"},
            "time_from": {"type": "string", "description": "HH:MM"},
            "time_to": {"type": "string", "description": "HH:MM"}}}}},
    {"type": "function", "function": {
        "name": "get_showtime_details",
        "description": "Seat availability and price of one showtime.",
        "parameters": {"type": "object", "properties": {"showtime_id": {"type": "string"}},
                       "required": ["showtime_id"]}}},
    {"type": "function", "function": {
        "name": "list_cinemas",
        "description": "List all cinemas with district and address.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "reserve_tickets",
        "description": "MOCK ticket reservation (no payment) for a specific showtime. Only call when "
                       "the user clearly asked to book and the showtime is unambiguous.",
        "parameters": {"type": "object", "properties": {
            "showtime_id": {"type": "string"}, "seats": {"type": "integer", "minimum": 1}},
            "required": ["showtime_id", "seats"]}}},
]
