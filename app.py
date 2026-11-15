import anthropic
import streamlit as st
from pypdf import PdfReader

MODEL = "claude-sonnet-5-5"

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
                "description": "One sentence: the overall verdict for a student.",
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
        },
        "required": ["summary", "clauses"],
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


uploaded = st.file_uploader("Upload your insurance contract (PDF)", type="pdf")

if uploaded:
    text = extract_text(uploaded)
    if not text.strip():
        st.error("No text found in this PDF (is it a scanned image?).")
        st.stop()
    st.success(f"Read {len(text):,} characters from {uploaded.name}.")
    with st.expander("See extracted text"):
        st.text(text)

    if st.button("🔍 Analyze my contract", type="primary"):
        with st.spinner("Reading the fine print…"):
            result = analyze(text, SYSTEM_PROMPT, MODEL)

        if "raw" in result:  # fallback: Claude answered in plain text
            st.markdown(result["raw"])
        else:
            clauses = sorted(
                result["clauses"], key=lambda c: SEVERITY_ORDER.get(c.get("severity"), 3)
            )
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
