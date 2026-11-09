# Run status — AI Lawyer prototype

Run date: 2026-11-09

## What was executed in this environment

- `pip install -r requirements.txt` — completed successfully; required packages were already installed.
- `python tests/test_guard.py` — passed (`guard tests: all passed`).
- `python run_tests.py --sleep 0` — completed all 10 test cases using the project's **offline mock provider** (`LLM_PROVIDER=mock`, `KB_DEV_MODE=0`).
- Knowledge base loader reports **13 verified entries out of 25 total entries**. The 13 verified entries are the P1 entries completed in the source pack. `wages-06` remains unverified and is not loaded in normal mode.

## Important limitation — not a live model run

No personal API key was supplied, so I did not call Gemini, Groq, Anthropic or OpenAI. The generated files in `outputs/` are raw **mock-provider smoke-test outputs**, not real AI responses. They are useful to confirm that the pipeline executes, but **do not submit these as the final raw outputs**.

The mock run's automatic checks returned `CHECK` for 9 of 10 cases and `PASS` for the out-of-scope case. This is expected to be treated as a mock limitation, not evidence that the live model fails. It also means the output-review step is not complete for the actual model.

## To complete the real run on your computer

1. Extract this ZIP and open the `ai-lawyer-india` folder in VS Code or a terminal.
2. Copy `.env.example` to `.env`.
3. In `.env`, keep `KB_DEV_MODE=0`, set `LLM_PROVIDER=gemini`, keep `LLM_MODEL=gemini-2.5-flash`, and paste your own key after `GEMINI_API_KEY=`. Never share or commit `.env`.
4. Run:
   ```bash
   pip install -r requirements.txt
   python tests/test_guard.py
   python run_tests.py
   ```
5. Review `outputs/summary.md` and every `outputs/*.md`. Keep the raw outputs unchanged. Only then should the real-model outputs be used in the submission.

Gemini API key creation and current model/pricing details are documented by Google: https://ai.google.dev/gemini-api/docs/api-key and https://ai.google.dev/gemini-api/docs/pricing

## Current result

The project installs and the guard unit tests pass. The full pipeline can execute offline, but live-model quality validation is still pending an API key and a real-provider run.
