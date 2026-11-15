# ClauseClair

**Pitch:** ClauseClair helps international students in Switzerland understand the home insurance contract they're about to sign (in French) by flagging the clauses that could cost them money and what to ask before signing.

**ONE core feature:** upload a contract PDF → list of risky clauses, each with: exact quote, severity (🔴/🟠/🟢), plain-English explanation, question to ask the insurer. Everything else is out of scope.

## Stack
- Streamlit (`app.py`), Anthropic Claude API, `pypdf` for text extraction
- Deployed on Streamlit Community Cloud from `main`
- API key in `st.secrets["ANTHROPIC_API_KEY"]` (local: `.streamlit/secrets.toml`, gitignored). Never in code.

## Rules
- Small testable steps, one commit per working step.
- Fictional documents only (`samples/`).
- Framing: help users *understand* contracts, not attack insurers (AXA is the jury).

## Status
- Where we are: feature freeze at T+1:05. App complete: upload + extraction + Claude analysis rendered as severity cards (tool use) + counts + sort; neutral verdict; sample-contract button; error handling (friendly st.error on API error, truncation + warning at 60,000 chars, `is_insurance_contract` flag -> warning instead of cards); welcome screen (hidden once a PDF is loaded); `clauses` returned as a string is json.loads-ed, else shown raw. README + screenshot done. Light theme + blue button (`.streamlit/config.toml`; the deployed app needs a reboot after changes). Demo video script written.
- Gotcha: keep `is_insurance_contract` AFTER `clauses` in the tool schema; placed first, Claude sometimes returned `clauses` as a string
- Next step: record the 1-min demo video (warm the cache first: run one analysis just before recording), then retro
