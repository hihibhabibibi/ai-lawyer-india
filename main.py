"""AI legal helper for everyday problems in India (rental deposit, consumer refund, unpaid wages).

Chat mode : python main.py --lang auto
One-shot  : python main.py --input story.txt --out outputs/result.md
"""
import argparse
from pathlib import Path

from src import intake, kb, pipeline
from src import prompts as P

MAX_QUESTIONS = 5                       # stop asking after this many follow-ups
SKIP_WORDS = {"done", "go", "skip", "enough", "bas"}   # user can type one of these to get the report now

BANNER = """=== AI Legal Helper (India) - information only, not a lawyer ===
I can help with: (1) rental deposit not returned, (2) refund / defective product or service, (3) unpaid salary.
Tell me what happened, in English, Hindi or Hinglish. Type 'done' any time to get your report, 'exit' to quit."""


def say(text):
    print("\nAssistant:", text)


def practice(result, lang):
    role = pipeline.TOPICS[result["case"]["topic"]]["role"]
    print(f"\n--- Practice mode: I will play the {role}. Make your argument. Type 'end' to get feedback. ---")
    convo = []
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in ("end", "exit", "quit"):
            break
        if user:
            convo.append({"role": "user", "content": user})
            reply = pipeline.practice_turn(result, lang, convo)
            convo.append({"role": "assistant", "content": reply})
            print(f"\n{role.title()}: {reply}")
    if convo:
        print("\n--- Feedback ---\n" + pipeline.practice_feedback(result, lang, convo))


def chat(args, entries):
    print(BANNER)
    if kb.dev_mode():
        print("\n" + P.DEV_BANNER)
    history, asked, lang = [], 0, ("en" if args.lang == "auto" else args.lang)
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in ("exit", "quit"):
            break
        if not user:
            continue
        wants_report = user.lower() in SKIP_WORDS
        if args.lang == "auto" and not wants_report:
            lang = intake.detect_language(user, lang)
        if not wants_report:
            history.append({"role": "user", "content": user})
        if not history:
            continue
        case = intake.extract_case(history, lang)

        if case["topic"] == "other":
            say(P.t(lang)["out_of_scope"])
            history, asked = [], 0
            continue
        if case["topic"] == "unknown" or (case["next_questions"] and asked < MAX_QUESTIONS and not wants_report):
            if asked >= MAX_QUESTIONS:
                say(P.t(lang)["unclear"])
                history, asked = [], 0
                continue
            question = "\n".join(case["next_questions"]) or P.t(lang)["ask_problem"]
            history.append({"role": "assistant", "content": question})
            asked += 1
            say(question)
            continue

        say("Thanks, I have enough. Preparing your case report (this takes a moment)...\n")
        user_text = " ".join(m["content"] for m in history if m["role"] == "user")
        result = pipeline.run_full(case, lang, entries, user_text)
        print(result["markdown"])
        try:
            if input("\nWant to practise arguing with the other side? (y/n): ").strip().lower().startswith("y"):
                practice(result, lang)
        except (EOFError, KeyboardInterrupt):
            break
        history, asked = [], 0
        print("\nYou can describe another problem, or type 'exit'.")


def one_shot(args, entries):
    story = Path(args.input).read_text(encoding="utf-8")
    lang = args.lang if args.lang != "auto" else intake.detect_language(story)
    result = pipeline.analyze([{"role": "user", "content": story}], lang, entries)
    print(result["markdown"])
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(result["markdown"], encoding="utf-8")
        print(f"\n[saved to {args.out}]")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", default="auto", choices=["auto", "en", "hi", "hinglish", "other"])
    ap.add_argument("--input", help="text file with one story (one-shot mode)")
    ap.add_argument("--out", help="where to save the one-shot result (markdown)")
    args = ap.parse_args()
    entries = kb.load_entries()
    one_shot(args, entries) if args.input else chat(args, entries)
