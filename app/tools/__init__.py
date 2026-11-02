"""
Tool registry: maps each domain to its functions and JSON schemas,
and runs a tool call safely (errors never reach the user as stack traces).
"""
import logging

from ..repositories import DataSourceError
from . import cinema, flights, shopping

log = logging.getLogger("superchat.tools")

DOMAINS = {
    "flights": flights,
    "shopping": shopping,
    "cinema": cinema,
}

# tool name -> domain name
TOOL_DOMAIN = {name: d for d, mod in DOMAINS.items() for name in mod.FUNCTIONS}


def schemas_for(domains: list[str]) -> list[dict]:
    out = []
    for d in domains:
        out += DOMAINS[d].SCHEMAS
    return out


def run_tool(ctx, name: str, args: dict) -> dict:
    domain = TOOL_DOMAIN.get(name)
    if domain is None:
        return {"error": f"Unknown tool {name}"}
    try:
        return DOMAINS[domain].FUNCTIONS[name](ctx, **args)
    except DataSourceError:
        log.exception("data source error in %s", name)
        return {"error": "The data source is temporarily unavailable."}
    except TypeError as e:  # wrong/missing arguments from the LLM
        log.warning("bad args for %s: %s (%s)", name, args, e)
        return {"error": f"Invalid arguments for {name}."}
    except Exception:  # never crash the chat
        log.exception("tool %s failed", name)
        return {"error": "Internal error while fetching data."}
