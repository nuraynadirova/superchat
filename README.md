# SuperChat — Phase 1 (mock data)

One chat for **flights**, **shopping** and **cinema**. Every message is routed automatically
(Flights / Shopping / Cinema / Mixed / Follow-up / Ambiguous / Out of scope), each domain keeps
its own state, and all facts come only from the official mock dataset in `data/`.

## Run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env   → then put your LLM key in .env
python run.py                      # open http://localhost:8000
```

Terminal chat instead of the browser: `python cli.py`

## Tests

```bash
python -m pytest -q                # offline tests: data layer, tools, orchestrator (fake LLM)
python tests/eval_routing.py       # routing accuracy with the real LLM → writes test_log.md
```

## Architecture

```
browser (app/static/index.html)
   │ POST /api/chat
app/main.py ── app/agent.py  (orchestrator)
                 ├─ app/router.py     LLM classifier → category + domains + language
                 │                    (keyword rules as fallback)
                 ├─ app/state.py      SessionState: shared + FlightState / ShoppingState / CinemaState
                 └─ app/tools/*.py    domain functions the LLM can call (function calling)
                        └─ app/repositories/   FlightRepository / ProductRepository / CinemaRepository
                                               JSON implementation now, real API in Phase 2
```

1. **Router** classifies the message using the session state and the last turns.
2. **Out of scope** → fixed polite refusal in the user's language. **Ambiguous** → one clarifying question.
3. Otherwise the **agent** gives the LLM only the tools of the selected domain(s); the LLM calls tools,
   tool results (never the LLM's own knowledge) are turned into a concise reply in the user's language.
4. Tools update the domain state (last results in shown order, selections, cart, reservations), which
   is how "the second one", "the cheaper one" and "back to the headphones" are resolved.

## Swapping data sources (Phase 2)

Add a class implementing the interface in `app/repositories/base.py` (e.g. `TravelpayoutsFlightRepository`)
that returns records in the same shape, register it in `app/repositories/__init__.py`, and set
`FLIGHT_SOURCE=api` in `.env`. No other code changes.

## LLM

Any OpenAI-compatible endpoint (Groq, Google Gemini, OpenAI, OpenRouter …) configured in `.env`.
Libraries: FastAPI, Uvicorn, OpenAI Python SDK, python-dotenv, pytest.
