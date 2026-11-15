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
a plain-English explanation of what it means in practice, and one concrete question to ask \
the insurer before signing.
Be fair and factual: help the user understand the contract, do not attack the insurer. \
Do not flag standard, harmless clauses. Answer in English."""

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
def analyze(contract_text: str) -> str:
    """Ask Claude to flag risky clauses. Cached: same text -> no second API call."""
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Here is the contract:\n\n{contract_text}"}],
    )
    return response.content[0].text


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
            result = analyze(text)
        st.markdown(result)
