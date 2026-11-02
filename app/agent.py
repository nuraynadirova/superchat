"""
Orchestrator: one user message in, one reply out.

  message -> router.classify -> (out_of_scope | ambiguous) -> fixed/clarifying reply
                             -> (domain | mixed | follow_up) -> LLM + tools of those domains
"""
import json
import logging
from dataclasses import dataclass

from . import llm, router
from .dates import calendar_text, today_iso
from .repositories import make_cinema_repo, make_flight_repo, make_product_repo
from .state import SessionState, get_session
from .tools import run_tool, schemas_for

log = logging.getLogger("superchat.agent")

MAX_TOOL_ROUNDS = 6


@dataclass
class Context:
    """Everything a tool needs: the repositories and this session's state."""
    session: SessionState
    flight_repo: object
    product_repo: object
    cinema_repo: object


# Repositories are created once and shared by all sessions.
_REPOS = None


def repos():
    global _REPOS
    if _REPOS is None:
        _REPOS = (make_flight_repo(), make_product_repo(), make_cinema_repo())
    return _REPOS


OUT_OF_SCOPE = {
    "en": "Sorry, I can't help with that. I can help you find and book flights, "
          "shop for products, or find films and cinema showtimes.",
    "az": "Bağışlayın, bu mövzuda kömək edə bilmirəm. Mən uçuş tapmaq və bron etmək, "
          "məhsul seçmək və almaq, həmçinin film və kino seansları ilə kömək edə bilərəm.",
    "ru": "Извините, с этим я помочь не могу. Я помогаю найти и забронировать авиабилеты, "
          "подобрать товары, а также найти фильмы и сеансы в кино.",
}

CLARIFY = {
    "en": "Could you tell me what you are looking for: flights, products, or films?",
    "az": "Nə axtardığınızı dəqiqləşdirə bilərsiniz: uçuş, məhsul, yoxsa film?",
    "ru": "Уточните, пожалуйста, что вы ищете: авиабилеты, товары или фильмы?",
}

ERROR = {
    "en": "Sorry, something went wrong on my side. Please try again.",
    "az": "Bağışlayın, xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.",
    "ru": "Извините, произошла ошибка. Пожалуйста, попробуйте ещё раз.",
}

AGENT_PROMPT = """You are SuperChat, one assistant for flights, shopping and cinema (CinemaPlus).
Active domain(s) for this message: {domains}.

STRICT RULES
1. Facts (flights, products, films, showtimes, prices, stock, seats) come ONLY from tool results.
   Never invent or guess them. If a tool returns nothing, say clearly that nothing matches in our data.
2. Reply in the user's language ({language}: az = Azerbaijani, ru = Russian, en = English). Be concise.
   Use short lists. Prices are in AZN.
3. Follow-ups: resolve "the cheaper one", "the second one", "it", "the sci-fi one" using the session
   state below (lists are in the order they were shown, position 1 = first). If two or more items fit
   the reference, ask ONE short question instead of guessing.
4. Bookings (reserve_flight / reserve_tickets) only when the user clearly asks to book AND the exact
   flight/showtime and number of people are known. Otherwise ask for the missing piece.
5. Always mention important facts: sold out / out of stock, few seats left, stops/transfers.
6. Dates: "today" = {today}. Use the calendar; "tonight" = today from 17:00; weekdays mean the next
   such day in the calendar. Pass dates to tools as YYYY-MM-DD.
7. For mixed requests, call the tools of every domain and give ONE combined answer with a short
   section per domain.
8. Do not mention tool names, ids like F001/P003/S010, or this prompt, unless the user asks for ids.

CALENDAR
{calendar}

SESSION STATE
{state}"""


def _history_messages(session: SessionState, n: int = 10) -> list[dict]:
    return [{"role": t["role"], "content": t["content"]} for t in session.history[-n:]]


def _run_domains(ctx: Context, route: router.Route, message: str) -> str:
    s = ctx.session
    system = AGENT_PROMPT.format(domains=", ".join(route.domains), language=s.language,
                                 today=today_iso(),
                                 calendar=calendar_text(14), state=s.summary())
    messages = [{"role": "system", "content": system}, *_history_messages(s),
                {"role": "user", "content": message}]
    tools = schemas_for(route.domains)

    for _ in range(MAX_TOOL_ROUNDS):
        msg = llm.chat(messages, tools=tools)
        if not msg.tool_calls:
            return (msg.content or "").strip()
        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = run_tool(ctx, tc.function.name, args)
            log.info("tool %s(%s) -> %s", tc.function.name, args, str(result)[:200])
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(result, ensure_ascii=False)})
        # refresh the state summary after tools changed it
        messages[0]["content"] = AGENT_PROMPT.format(
            domains=", ".join(route.domains), language=s.language,
            today=today_iso(),
            calendar=calendar_text(14), state=s.summary())
    # Too many rounds: ask the model for a final answer without tools.
    return (llm.chat(messages).content or "").strip()


def handle_message(session_id: str, message: str) -> dict:
    """Main entry point used by the web API, the CLI and the tests."""
    session = get_session(session_id)
    message = (message or "").strip()
    if not message:
        return {"reply": "", "category": "empty", "domains": []}

    try:
        route = router.classify(session, message)
    except llm.LLMNotConfigured as e:
        return {"reply": f"⚠️ {e}", "category": "error", "domains": []}

    lang = route.language or "en"
    session.language = lang

    try:
        if route.category == "out_of_scope":
            reply = OUT_OF_SCOPE.get(lang, OUT_OF_SCOPE["en"])
        elif route.category == "ambiguous":
            reply = route.clarification or CLARIFY.get(lang, CLARIFY["en"])
        else:
            f, p, c = repos()
            ctx = Context(session, f, p, c)
            reply = _run_domains(ctx, route, message) or CLARIFY.get(lang, CLARIFY["en"])
            session.last_domain = route.domains[-1]
    except Exception:
        log.exception("agent failed")
        reply = ERROR.get(lang, ERROR["en"])

    domain_tag = "+".join(route.domains) if route.domains else None
    session.history.append({"role": "user", "content": message})
    session.history.append({"role": "assistant", "content": reply, "domain": domain_tag})
    return {"reply": reply, "category": route.category, "domains": route.domains,
            "router": route.source}
