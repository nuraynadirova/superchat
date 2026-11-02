"""
Routing: decides, for every user message, which category it belongs to.

Hybrid approach:
  1. LLM classifier (main): understands follow-ups, mixed intents, all languages.
  2. Keyword rules (fallback): used if the LLM call fails or returns invalid JSON,
     so the chat keeps working.
"""
import json
import logging
import re
from dataclasses import dataclass, field

from . import llm
from .dates import calendar_text
from .state import SessionState

log = logging.getLogger("superchat.router")

CATEGORIES = ["flights", "shopping", "cinema", "mixed", "follow_up", "ambiguous", "out_of_scope"]
DOMAINS = ["flights", "shopping", "cinema"]


@dataclass
class Route:
    category: str
    domains: list[str] = field(default_factory=list)
    language: str = "en"
    clarification: str | None = None   # question to ask when ambiguous
    source: str = "llm"                # "llm" or "rules"


ROUTER_PROMPT = """You are the router of SuperChat, an assistant that covers exactly three domains:
- flights: searching/comparing flights, dates, prices, airlines, baggage, booking a flight
- shopping: products (electronics, audio, phones, laptops, watches, shoes, backpacks, coffee machines, games), prices, stock, cart
- cinema: films, genres, cinemas, showtimes, seats, ticket booking

Classify the LATEST user message into exactly one category:
- "flights" / "shopping" / "cinema": a new, self-contained request for that domain
- "mixed": one message with intents for two or more domains (e.g. a flight AND a backpack)
- "follow_up": a short message that only makes sense with earlier context ("the cheaper one",
  "and for Saturday?", "is it in stock?", "the second one", "book it" when something is selected,
  "back to the headphones"). Put the domain it refers to in "domains".
- "ambiguous": cannot be assigned confidently to a domain, and earlier context does not resolve it
  (e.g. "show me something good", or "book two seats" with no earlier flight/cinema context).
  Write ONE short clarifying question in the user's language in "clarification".
- "out_of_scope": unrelated to flights, shopping and cinema (weather, news, maths, jokes...).

Rules:
- "domains" lists the domain(s) needed: one for flights/shopping/cinema/follow_up, 2+ for mixed,
  empty for ambiguous/out_of_scope.
- A follow-up may return to an OLDER domain, not only the last one. Example: after a shopping turn,
  "and the sci-fi one, any seats on Saturday?" is follow_up with domains ["cinema"].
- "seats" alone is ambiguous between cinema and flights unless context decides.
- "language": the language of the latest user message: "az" (Azerbaijani), "ru" (Russian),
  "en" (English) or another ISO code.

Current session state:
{state}

Calendar (dates resolve against it):
{calendar}

Reply with ONLY a JSON object, no other text:
{{"category": "...", "domains": [...], "language": "..", "clarification": null}}"""


def classify(session: SessionState, message: str) -> Route:
    recent = session.history[-6:]
    convo = "\n".join(f"{t['role'].upper()}"
                      f"{' [' + t['domain'] + ']' if t.get('domain') else ''}: {t['content'][:300]}"
                      for t in recent) or "(no earlier messages)"
    messages = [
        {"role": "system", "content": ROUTER_PROMPT.format(state=session.summary(),
                                                           calendar=calendar_text(7))},
        {"role": "user", "content": f"Earlier conversation:\n{convo}\n\nLATEST USER MESSAGE:\n{message}"},
    ]
    try:
        raw = llm.chat(messages, temperature=0).content or ""
        data = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        cat = data.get("category")
        if cat not in CATEGORIES:
            raise ValueError(f"bad category {cat}")
        domains = [d for d in data.get("domains") or [] if d in DOMAINS]
        if cat in DOMAINS and not domains:
            domains = [cat]
        if cat in ("mixed", "follow_up") and not domains:
            cat = "ambiguous"
        return Route(cat, domains, data.get("language") or "en", data.get("clarification"))
    except llm.LLMNotConfigured:
        raise
    except Exception as e:
        log.warning("LLM routing failed (%s); falling back to rules", e)
        return classify_rules(session, message)


# ---------------------------------------------------------------- rule fallback
KEYWORDS = {
    "flights": ["flight", "fly", "airline", "ticket to", "baggage", "uçuş", "reys", "aviabilet",
                "təyyarə", "рейс", "перелёт", "перелет", "авиабилет", "самолёт", "багаж",
                "istanbul", "dubai", "moscow", "tbilisi", "tashkent", "стамбул", "дубай"],
    "shopping": ["product", "buy", "price of", "cart", "stock", "headphone", "earbud", "laptop",
                 "phone", "watch", "speaker", "shoe", "backpack", "coffee", "game", "səbət",
                 "qulaqlıq", "noutbuk", "telefon", "çanta", "almaq", "корзин", "наушник", "ноутбук",
                 "телефон", "рюкзак", "купить", "товар"],
    "cinema": ["film", "movie", "cinema", "showtime", "playing", "kino", "seans", "кино",
               "фильм", "сеанс", "sci-fi", "comedy", "horror", "komediya", "комеди"],
}


def detect_language(text: str) -> str:
    if re.search(r"[а-яё]", text.lower()):
        return "ru"
    if re.search(r"[əğıöüşç]", text.lower()):
        return "az"
    return "en"


def classify_rules(session: SessionState, message: str) -> Route:
    text = message.lower()
    hits = [d for d, words in KEYWORDS.items() if any(w in text for w in words)]
    lang = detect_language(message)
    if len(hits) == 1:
        return Route(hits[0], hits, lang, source="rules")
    if len(hits) > 1:
        return Route("mixed", hits, lang, source="rules")
    if session.last_domain and len(text.split()) <= 8:
        return Route("follow_up", [session.last_domain], lang, source="rules")
    return Route("ambiguous", [], lang, source="rules")
