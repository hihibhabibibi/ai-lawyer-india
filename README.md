# AI Legal Helper for India (command-line prototype)

An honest, grounded legal-information assistant for **three everyday problems**:
1. Landlord not returning a rental security deposit
2. Refund / defective product or service not provided (consumer complaint)
3. Unpaid salary / wages

Anything else is declined politely with general direction and free legal aid (DLSA, NALSA helpline 15100).
It is **not a lawyer** and says so, and says when you need a real one.

It works in English, Hindi and Hinglish: it detects your language and replies in it. It collects the story with one or
two short questions at a time, builds a timeline and evidence checklist, explains options, drafts a notice, and can
play the other side so you can practise.

## How it avoids inventing law

1. **Closed-book legal basis.** The model sees only entries from `kb/` that a human has marked `VERIFIED` (with official source URL and verification date). Entries still containing `TODO` are never loaded.
2. **Cite by ID, not by memory.** The model may cite law only as `[KB:id]`. Code swaps each id for the act and section stored in the KB, so the model never types a section number itself.
3. **Regex backstop (`src/guard.py`).** After every generation (report, draft, practice replies, feedback) we scan for section numbers, act names, case citations ("X v. Y", AIR/SCC) and web links. Anything not in the retrieved KB entries is replaced by `[unverified legal reference removed]` and counted in the "Safety check" footer. Case law is always removed: the KB holds no judgments.
4. **No KB, no law.** If the KB has nothing for the topic, the answer says "I'm not sure about the exact legal provision here", names no law, forum or time limit, and recommends a lawyer / legal aid.
5. **Lawyer-needed rules in plain code (`src/risk.py`).** Large amount, court summons/notice already issued, police or criminal angle, threats, old claim (time limit may have passed), or conflicting facts: a clear "please see a lawyer / DLSA" box is added and confidence drops to Low.
6. **"Sources used" footer** lists every KB entry cited, with its URL and last-verified date.

Known limits are in the solution doc and `failures_log.md`. Short version: the guard cannot catch a wrong *claim* that has no section number (for example a made-up time limit written in words), so the prompt forbids it and humans should review.

## Setup

```bash
git clone <your-repo-url> && cd ai-lawyer-india
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env: choose provider, model, add ONE API key
```
Free option: a Gemini key from Google AI Studio (`LLM_PROVIDER=gemini`) or a Groq key (`LLM_PROVIDER=groq`).
Swap models by changing `LLM_PROVIDER` / `LLM_MODEL` in `.env` (Anthropic, Gemini, Groq, or any OpenAI-compatible server via `LLM_PROVIDER=openai` + `LLM_BASE_URL`). Nothing else changes.

Quick check that your key works: `python -c "from src.llm import call_llm; print(call_llm([{'role':'user','content':'Say hi'}]))"`

## Before you get useful answers: fill the knowledge base

Open `kb/*.json`. Every entry starts as `TODO` with an UNVERIFIED suggestion. For each entry you can confirm from the official text (indiacode.nic.in or another official source): fill `act`, `section`, `summary_plain` (your own plain words), `source_url`, `last_verified`, then set `"status": "VERIFIED"`. See `VERIFY_CHECKLIST.md` for the order (P1 first).
With zero verified entries the assistant still runs but, by design, names no law at all.

## Run

```bash
# 1. Interactive chat (type 'done' to get the report early, 'exit' to quit)
python main.py --lang auto            # or --lang en | hi | hinglish

# 2. One-shot: a single messy story from a text file (good for an interview)
python main.py --input story.txt --out outputs/result.md

# 3. Tests
python tests/test_guard.py            # offline unit tests of the hallucination guard (no API key needed)
python run_tests.py                   # all 10 cases through the full pipeline -> outputs/ (needs your API key)
python run_tests.py --only con-3      # a single case
```
`run_tests.py` writes one raw `.md` and one `.json` per case plus `outputs/summary.md` (which also states how many KB entries were verified). Do not edit those files; record what went wrong in `failures_log.md`.

Offline smoke test with no API key (fake model, output is nonsense by design): `LLM_PROVIDER=mock python run_tests.py --out /tmp/mock_out`.
`KB_DEV_MODE=1` also loads UNVERIFIED entries so you can see the whole flow before verifying. Never use it for submitted outputs.

## Files

```
main.py             chat mode and one-shot mode
run_tests.py        runs tests/cases.json, saves raw outputs + summary
kb/                 one JSON per topic (+ general): verified law entries only
src/llm.py          call_llm(messages, system): provider/model from env vars
src/kb.py           loads KB, keyword retrieval
src/intake.py       language detection, topics, story -> structured case file
src/risk.py         "you need a real lawyer" rules
src/guard.py        [KB:id] expansion + regex hallucination check + sources footer
src/pipeline.py     report -> draft notice -> pushback preview, practice mode
src/prompts.py      every prompt and every fixed message (en / hi / hinglish)
tests/cases.json    10 test cases (3 per topic, 1 out of scope; includes a trap and Hindi/Hinglish)
tests/test_guard.py offline guard tests
outputs/            raw outputs from run_tests.py
failures_log.md     template for recording what went wrong
VERIFY_CHECKLIST.md every legal claim you must verify
```

## Sample output (FORMAT ONLY)

> This sample comes from the **offline mock model in dev mode**, so the text is nonsense on purpose. It deliberately writes a fake section, act, case and link to show the guard removing them. **Replace it with your first real run** after you verify the KB.

```
# Rental security deposit not returned

> **DEV MODE: this answer uses UNVERIFIED knowledge-base entries. It is for testing the flow only. Do not submit it or rely on it.**

## (mock) What happened
This is fake text from the offline mock model.

## (mock) Where you stand
You may have a claim (Model Tenancy Act, 2021 (a MODEL law: binding only where a state has adopted it), Security-deposit provision (maybe Sec 11 - check) - UNVERIFIED). Under [unverified legal reference removed] of the [unverified legal reference removed] you will surely win, as the court held in [unverified legal reference removed] [unverified legal reference removed]. See [unverified legal reference removed] .

## (mock) Your options
1. Talk to them. 2. Send a notice.

## Draft notice (review before sending)
Below is a first draft in English that you can adapt.

[... draft notice and pushback sections omitted here ...]

## Sources used
- **deposit-01**: Model Tenancy Act, 2021 (a MODEL law: binding only where a state has adopted it), Security-deposit provision (maybe Sec 11 - check). (summary not written yet - student TODO) Source: TODO (last verified: UNVERIFIED)

## Safety check
Confidence: **Low**

15 unverified legal reference(s) were removed automatically (section x3, act x3, case x6, url x3).

**Details that would help me give better guidance:**
- (mock) When did this start?

---
_This is general information to help you understand your situation. It is not legal advice and not a substitute for a lawyer._
```

## Scaling to more topics and languages

New topic = one `kb/<topic>.json`, one entry in `TOPICS` (`src/intake.py`: label, other-side role, evidence list, notice type) and the extractor's topic list. New language = a block in `src/prompts.py` (`T`) and a detection rule; the model already writes the free text in the user's language.
