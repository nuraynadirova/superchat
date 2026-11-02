"""
Tests the orchestrator plumbing with a FAKE LLM (no API key needed):
router -> tool call -> tool result -> final answer, plus error handling.
"""
import json
from types import SimpleNamespace

from app import agent, llm, router
from app.state import reset_session


def _tool_call(name, args, id_="call_1"):
    tc = SimpleNamespace(id=id_, type="function",
                         function=SimpleNamespace(name=name, arguments=json.dumps(args)))
    tc.model_dump = lambda: {"id": id_, "type": "function",
                             "function": {"name": name, "arguments": json.dumps(args)}}
    return tc


def _msg(content=None, tool_calls=None):
    return SimpleNamespace(content=content, tool_calls=tool_calls)


def test_full_turn_with_fake_llm(monkeypatch):
    script = iter([
        _msg('{"category": "flights", "domains": ["flights"], "language": "en"}'),          # router
        _msg(tool_calls=[_tool_call("search_flights", {"destination": "Istanbul", "date": "2026-11-06"})]),
        _msg("Found 3 flights; the cheapest is 175 AZN with 1 stop."),                      # final
    ])
    seen = []

    def fake_chat(messages, tools=None, temperature=0.1):
        seen.append(messages)
        return next(script)

    monkeypatch.setattr(llm, "chat", fake_chat)
    reset_session("t1")
    r = agent.handle_message("t1", "Flights to Istanbul on 6 November")
    assert r["category"] == "flights"
    assert "175" in r["reply"]
    tool_msg = seen[-1][-1]
    assert tool_msg["role"] == "tool" and "F013" in tool_msg["content"]
    assert agent.get_session("t1").last_domain == "flights"


def test_out_of_scope_and_language(monkeypatch):
    monkeypatch.setattr(llm, "chat", lambda *a, **k: _msg(
        '{"category": "out_of_scope", "domains": [], "language": "az"}'))
    reset_session("t2")
    r = agent.handle_message("t2", "Gəncədə hava necədir?")
    assert r["category"] == "out_of_scope" and "uçuş" in r["reply"]


def test_router_falls_back_to_rules_on_garbage(monkeypatch):
    monkeypatch.setattr(llm, "chat", lambda *a, **k: _msg("I think it's about films"))
    reset_session("t3")
    route = router.classify(agent.get_session("t3"), "Какие фильмы идут сегодня?")
    assert route.source == "rules" and route.domains == ["cinema"] and route.language == "ru"


def test_llm_crash_gives_friendly_error(monkeypatch):
    calls = {"n": 0}

    def flaky(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            return _msg('{"category": "shopping", "domains": ["shopping"], "language": "en"}')
        raise RuntimeError("provider down")

    monkeypatch.setattr(llm, "chat", flaky)
    reset_session("t4")
    r = agent.handle_message("t4", "Show me laptops")
    assert "Traceback" not in r["reply"] and "went wrong" in r["reply"]
