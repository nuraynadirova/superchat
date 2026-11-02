"""Chat in the terminal (handy for quick tests):  python cli.py"""
from app.agent import handle_message

if __name__ == "__main__":
    print("SuperChat CLI. Type 'exit' to quit.\n")
    while True:
        try:
            text = input("You: ")
        except (EOFError, KeyboardInterrupt):
            break
        if text.strip().lower() in ("exit", "quit"):
            break
        r = handle_message("cli", text)
        print(f"[{r['category']} {'+'.join(r['domains'])}]")
        print(f"Bot: {r['reply']}\n")
