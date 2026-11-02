"""
Routing evaluation (needs a working LLM key in .env).

Runs every conversation in routing_cases.json through the REAL pipeline
(so state builds up turn by turn), compares the router's category/domains with
the expected labels and writes test_log.md with accuracy figures and errors.

Run:  python tests/eval_routing.py                      -> routing_cases.json      -> test_log.md
      python tests/eval_routing.py routing_cases_hard.json -> routing_cases_hard.json -> test_log_hard.md
"""
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.agent import handle_message  # noqa: E402
from app.config import settings  # noqa: E402
from app.state import reset_session  # noqa: E402


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "routing_cases.json"
    cases = json.loads((Path(__file__).parent / Path(name).name).read_text(encoding="utf-8"))
    suffix = Path(name).stem.replace("routing_cases", "")
    log_file = ROOT / f"test_log{suffix}.md"
    rows = []
    for conv in cases:
        sid = f"eval-{conv['id']}"
        reset_session(sid)
        for i, turn in enumerate(conv["turns"], 1):
            t0 = time.time()
            r = handle_message(sid, turn["user"])
            rows.append({
                "conv": conv["id"], "turn": i, "lang": conv["lang"], "user": turn["user"],
                "exp_cat": turn["category"], "got_cat": r["category"],
                "exp_dom": sorted(turn["domains"]), "got_dom": sorted(r["domains"]),
                "router": r.get("router"), "reply": r["reply"], "sec": round(time.time() - t0, 1),
            })
            ok = "OK " if rows[-1]["exp_cat"] == rows[-1]["got_cat"] else "ERR"
            print(f"{ok} {conv['id']}.{i} [{r['category']}] {turn['user']}")
            time.sleep(float(os.getenv("EVAL_DELAY", "2")))

    def cat_ok(r):
        return r["exp_cat"] == r["got_cat"]

    def full_ok(r):
        return cat_ok(r) and r["exp_dom"] == r["got_dom"]

    n = len(rows)
    by_cat, by_lang = defaultdict(list), defaultdict(list)
    for r in rows:
        by_cat[r["exp_cat"]].append(r)
        by_lang[r["lang"]].append(r)
    confusion = Counter((r["exp_cat"], r["got_cat"]) for r in rows)

    out = [f"# SuperChat — Routing test log ({Path(name).name})", "",
           f"Model: `{settings.llm_model}` · Reference date: {settings.reference_date} · "
           f"Turns: {n} in {len(cases)} conversations", "",
           "## Accuracy", "",
           f"- Category accuracy: **{sum(map(cat_ok, rows))}/{n} = {sum(map(cat_ok, rows)) / n:.1%}**",
           f"- Category + domains accuracy: **{sum(map(full_ok, rows))}/{n} = {sum(map(full_ok, rows)) / n:.1%}**",
           f"- Rule fallback used: {sum(r['router'] == 'rules' for r in rows)} times",
           f"- Average latency per turn: {sum(r['sec'] for r in rows) / n:.1f} s", "",
           "### By category", "", "| Category | Correct | Total | Accuracy |", "|---|---|---|---|"]
    for c, rs in sorted(by_cat.items()):
        k = sum(map(cat_ok, rs))
        out.append(f"| {c} | {k} | {len(rs)} | {k / len(rs):.0%} |")
    out += ["", "### By language", "", "| Language | Correct | Total | Accuracy |", "|---|---|---|---|"]
    for lang, rs in sorted(by_lang.items()):
        k = sum(map(full_ok, rs))
        out.append(f"| {lang} | {k} | {len(rs)} | {k / len(rs):.0%} |")
    out += ["", "### Confusion (expected → predicted, errors only)", ""]
    errs = [(e, g, k) for (e, g), k in confusion.items() if e != g]
    out += [f"- {e} → {g}: {k}" for e, g, k in sorted(errs)] or ["- none"]
    out += ["", "## Errors", ""]
    bad = [r for r in rows if not full_ok(r)]
    for r in bad:
        out.append(f"- **{r['conv']}.{r['turn']}** ({r['lang']}) “{r['user']}” — expected "
                   f"`{r['exp_cat']} {r['exp_dom']}`, got `{r['got_cat']} {r['got_dom']}`")
    if not bad:
        out.append("- none")
    out += ["", "## Error analysis", "", "_Write 3–5 sentences here: why the errors happened and "
            "what you changed (prompt, rules, examples)._", "",
            "## Full transcript", ""]
    for r in rows:
        out.append(f"**{r['conv']}.{r['turn']}** User: {r['user']}  \n"
                   f"`{r['got_cat']} {r['got_dom']}` Bot: {r['reply'][:400].replace(chr(10), ' ')}\n")

    log_file.write_text("\n".join(out), encoding="utf-8")
    print(f"\nCategory accuracy {sum(map(cat_ok, rows))}/{n}. Report written to {log_file.name}")


if __name__ == "__main__":
    main()
