import json
from pathlib import Path

import anthropic
import streamlit as st
from pypdf import PdfReader

MODEL = "claude-sonnet-5-5"
SAMPLE_PDF = Path(__file__).parent / "samples" / "contrat_assurance_menage_fictif.pdf"
MAX_CHARS = 60_000  # longer contracts are truncated to keep cost and latency reasonable

SYSTEM_PROMPT = """You help international students in Switzerland understand the home \
insurance contract (inventaire du ménage + responsabilité civile privée) they are about to sign.
The contract is usually in French; the student may not read French well.

Identify the clauses that could cost the student money or surprise them later \
(exclusions, deductibles, renewal and cancellation terms, deadlines, premium changes, data use...).
For each one give: the exact quote in French, a severity (high / medium / low), \
a short plain-English explanation of what it means in practice (2-3 sentences, concrete examples \
from student life), and one concrete question to ask the insurer before signing.
Severity must help the student prioritise, so reserve "high" for the few worst clauses:
- high: in a common student situation, can cost well over CHF 1'000 or remove cover entirely. \
Usually only 2-4 clauses in a contract deserve this.
- medium: a real but limited cost or inconvenience.
- low: unusual or slightly unfavourable, worth knowing but not a deal-breaker.
Be fair and factual: help the user understand the contract, do not attack the insurer. \
Do not flag standard, harmless clauses. Answer in English.
The summary must be neutral and factual, addressed to the student ("you"): never say whether \
you would sign; instead point to what to clarify or compare before signing.
If the document is not an insurance contract, set is_insurance_contract to false \
and leave clauses empty.
Always report your findings by calling the report_clauses tool."""

# Tool use = a way to get Claude's answer as structured JSON matching this schema.
REPORT_TOOL = {
    "name": "report_clauses",
    "description": "Report the risky clauses found in the insurance contract.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "One neutral sentence for the student: the main points to clarify before signing.",
            },
            "clauses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "article": {"type": "string", "description": "e.g. 'Art. 8'"},
                        "title": {"type": "string", "description": "Short English title"},
                        "quote": {"type": "string", "description": "Exact quote in French"},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                        "explanation": {"type": "string"},
                        "question": {"type": "string", "description": "Question to ask the insurer"},
                    },
                    "required": ["article", "title", "quote", "severity", "explanation", "question"],
                },
            },
            "is_insurance_contract": {
                "type": "boolean",
                "description": "True if the document is an insurance contract, false if it is something else.",
            },
        },
        "required": ["summary", "clauses", "is_insurance_contract"],
    },
}

SEVERITY_ICON = {"high": "🔴", "medium": "🟠", "low": "🟢"}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

st.set_page_config(page_title="ClauseClair", page_icon="🛡️")

st.title("🛡️ ClauseClair")
st.write(
    "Understand the Swiss home insurance contract you're about to sign — "
    "before it costs you money."
)


def extract_text(pdf_file) -> str:
    """Return all the text of an uploaded PDF, page by page."""
    reader = PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


@st.cache_data(show_spinner=False)
def analyze(contract_text: str, system_prompt: str, model: str) -> dict:
    """Ask Claude to flag risky clauses.

    Cached on (function code + arguments). The prompt and model are passed as arguments
    so that changing them invalidates the cache (globals are NOT part of the cache key).

    Returns {"summary": str, "clauses": [...]} or, if Claude didn't use the tool,
    {"raw": str} so we can still show something.
    """
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=model,
        max_tokens=8000,
        system=system_prompt,
        tools=[REPORT_TOOL],
        messages=[{"role": "user", "content": f"Here is the contract:\n\n{contract_text}"}],
    )
    # The response is a list of blocks (thinking, text, tool_use...). Look for our tool call.
    for block in response.content:
        if block.type == "tool_use" and block.name == "report_clauses":
            return block.input
    text = "".join(block.text for block in response.content if block.type == "text")
    return {"raw": text or f"No answer (stop_reason: {response.stop_reason})."}


def show_clause(clause: dict) -> None:
    icon = SEVERITY_ICON.get(clause.get("severity"), "⚪")
    with st.container(border=True):
        st.markdown(f"#### {icon} {clause['article']} — {clause['title']}")
        st.caption(f"« {clause['quote']} »")
        st.markdown(f"**In practice:** {clause['explanation']}")
        st.info(f"**Ask the insurer:** {clause['question']}", icon="💬")


welcome = st.container()  # filled below, only while no PDF is loaded

uploaded = st.file_uploader("Upload your insurance contract (PDF)", type="pdf")

# A button is True only during the rerun right after the click, so we remember
# the choice in session_state (it survives the next click on "Analyze").
if st.button("📄 No contract at hand? Try a sample (fictional)"):
    st.session_state.use_sample = True

if uploaded:
    pdf_source, pdf_name = uploaded, uploaded.name
elif st.session_state.get("use_sample"):
    pdf_source, pdf_name = SAMPLE_PDF, "the sample contract (fictional)"
else:
    pdf_source = None
    with welcome:
        for col, (title, body) in zip(
            st.columns(3),
            [
                ("📄 1. Upload", "Your contract, as a PDF, in French."),
                ("🔍 2. Understand", "Risky clauses ranked 🔴🟠🟢, explained in plain English."),
                ("💬 3. Ask", "The right questions to ask the insurer before you sign."),
            ],
        ):
            with col:
                st.markdown(f"**{title}**")
                st.write(body)

if pdf_source:
    text = extract_text(pdf_source)
    if not text.strip():
        st.error("No text found in this PDF (is it a scanned image?).")
        st.stop()
    st.success(f"Read {len(text):,} characters from {pdf_name}.")
    with st.expander("See extracted text"):
        st.text(text)

    if len(text) > MAX_CHARS:
        st.warning(
            f"This document is very long: only the first {MAX_CHARS:,} characters will be analyzed."
        )
        text = text[:MAX_CHARS]

    if st.button("🔍 Analyze my contract", type="primary"):
        try:
            with st.spinner("Reading the fine print…"):
                result = analyze(text, SYSTEM_PROMPT, MODEL)
        except anthropic.APIError:
            st.error(
                "Sorry, the analysis service is unavailable right now. Please try again in a minute."
            )
            st.stop()

        clauses = result.get("clauses")
        if isinstance(clauses, str):  # Claude sometimes returns the list as a JSON string
            try:
                clauses = json.loads(clauses)
            except ValueError:
                pass

        if "raw" in result:  # fallback: Claude answered in plain text
            st.markdown(result["raw"])
        elif not result.get("is_insurance_contract", True):
            st.warning("This doesn't look like an insurance contract")
        elif not isinstance(clauses, list):  # malformed answer: show it rather than crash
            st.markdown(str(result.get("clauses") or result))
        else:
            clauses = sorted(clauses, key=lambda c: SEVERITY_ORDER.get(c.get("severity"), 3))
            st.subheader(result["summary"])
            # Summary row: how many clauses of each severity
            for col, (sev, label) in zip(
                st.columns(3), [("high", "High risk"), ("medium", "Medium"), ("low", "Low")]
            ):
                count = sum(c.get("severity") == sev for c in clauses)
                col.metric(f"{SEVERITY_ICON[sev]} {label}", count)
            for clause in clauses:
                show_clause(clause)

        st.caption("ClauseClair helps you understand your contract. It is not legal advice.")
