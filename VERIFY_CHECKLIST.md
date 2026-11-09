# Every legal claim you must verify

Source of truth = official text (indiacode.nic.in, egazette, nalsa.gov.in, consumer/labour department portals). My suggestions in `kb/*.json` came from an AI's memory and may be wrong or outdated. For each item: open the official text, fill the KB entry (act, section, summary_plain in your own words, source_url, last_verified), set status to `VERIFIED`.
**Do P1 first (about 12 entries gets a working demo). P2 if time allows. Any entry you skip is simply never used.**

## Rental deposit (`kb/rental_deposit.json`)
- [ ] P1 deposit-01 Model Tenancy Act 2021: is it in force in the states you test? deposit cap, refund timeline, section number
- [ ] P1 deposit-03 Indian Contract Act 1872: which section genuinely fits a refused deposit (I guessed Sec 73)
- [ ] P1 deposit-04 Limitation Act 1963: Article and period for recovering money, and when it starts
- [ ] P2 deposit-02 State rent act for 1-2 states only (does it even mention deposits? say so if not)
- [ ] P2 deposit-05 CPC: is a summary suit (Order XXXVII) really available for deposits?
- [ ] P2 deposit-06 Which civil / small-causes court, by state and value

## Consumer refund (`kb/consumer_refund.json`)
- [ ] P1 consumer-01 Consumer Protection Act 2019 definitions (consumer, defect, deficiency): section numbers
- [ ] P1 consumer-03 District Commission jurisdiction and the CURRENT money limits (Jurisdiction Rules 2021 and any later change)
- [ ] P1 consumer-04 How to file (section, e-Daakhil portal, fee slabs); **is a prior legal notice compulsory? (I believe not; verify)**
- [ ] P1 consumer-05 Limitation for a complaint (I think 2 years; verify period, start, delay condonation)
- [ ] P1 consumer-06 What the commission can order (refund, replacement, compensation)
- [ ] P2 consumer-02 Unfair trade practice definition
- [ ] P2 consumer-07 E-Commerce Rules 2020 (online sellers' duties)
- [ ] P2 consumer-08 National Consumer Helpline: official number and portal (do not trust memory)

## Unpaid wages (`kb/unpaid_wages.json`)
- [ ] P1 wages-01 Code on Wages 2019: **is it in force and from what date?** which older acts it replaced; time limit for paying wages (incl. after leaving the job)
- [ ] P1 wages-02 Claim route for unpaid wages: section, authority, time limit for the claim
- [ ] P1 wages-06 Which labour office / portal an employee actually uses
- [ ] P2 wages-03 Payment of Wages Act 1936: repealed? Only for old periods?
- [ ] P2 wages-04 Industrial Relations Code 2020: does it matter for ordinary unpaid salary?
- [ ] P2 wages-05 State Shops and Establishments Act for the state(s) you test

## General (`kb/general.json`)
- [ ] P1 general-01 NALSA helpline 15100 and DLSA details (nalsa.gov.in). Note: 15100 is also hard-coded in `src/prompts.py` messages
- [ ] P1 general-02 Legal Services Authorities Act 1987: who is eligible for free legal aid (section)
- [ ] P1 general-03 Limitation Act 1963: the general principle that delay can bar a claim
- [ ] P2 general-04 Lok Adalat / pre-litigation settlement
- [ ] P2 general-05 Is a legal notice legally required before suing? (differs by claim type)

## Product choices in code (not law, but know them for the interview)
- [ ] `src/risk.py`: HIGH_AMOUNT_INR = 5,00,000 and OLD_AFTER_YEARS = 2 are my product choices, not legal limits. The message says "may be past a time limit" and never states the real limit.
- [ ] Practical evidence lists in `src/intake.py` (what proof to gather) are practical advice, not law. Read them once.
- [ ] 15100 appears in the fixed out-of-scope message (3 languages). Re-check the number.
- [ ] Hindi / Hinglish fixed texts in `src/prompts.py`: have a Hindi-speaking friend read them once.

## After the first real run
- [ ] Read EVERY output in outputs/. For each section number, act, website or time limit you see, confirm it is in "Sources used" and in the KB. Log problems in `failures_log.md`.
- [ ] Check the trap case (con-3) and oos-1 by hand.
- [ ] Replace the mock sample in README with a real output snippet.
