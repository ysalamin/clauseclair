import streamlit as st
from pypdf import PdfReader

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


uploaded = st.file_uploader("Upload your insurance contract (PDF)", type="pdf")

if uploaded:
    text = extract_text(uploaded)
    if not text.strip():
        st.error("No text found in this PDF (is it a scanned image?).")
        st.stop()
    st.success(f"Read {len(text):,} characters from {uploaded.name}.")
    with st.expander("See extracted text"):
        st.text(text)
