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
- Where we are: hello-world deployed at clauseclair.streamlit.app; upload + extraction + Claude analysis rendered as severity cards (tool use) + counts + sort; neutral verdict; sample-contract button
- Next step: B) error handling (API error, long PDF, not a contract) then C) welcome screen
