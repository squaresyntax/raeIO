import streamlit as st
import yaml
import logging
from raeio_agent import RAEIOAgent
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

logger = logging.getLogger("RAEIO_UI")

if "agent" not in st.session_state:
    st.session_state["agent"] = RAEIOAgent(config, logger)
agent = st.session_state["agent"]

# Custom CSS for Bank Gothic, white text, black background, deep purple buttons
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
html, body, [class*="css"]  {
    background-color: #000 !important;
    color: #fff !important;
    font-family: 'Bank Gothic', 'Share Tech Mono', monospace !important;
}
.stButton>button {
    background-color: #222 !important;
    color: #fff !important;
    border-radius: 3px;
    border: 2px solid #6C1E90 !important;
    font-family: 'Bank Gothic', 'Share Tech Mono', monospace !important;
}
.stButton>button:active, .stButton>button:focus {
    background-color: #6C1E90 !important;
    color: #fff !important;
    border: 2px solid #fff !important;
}
</style>
""", unsafe_allow_html=True)

categories = [
    "Art", "Sound", "Video", "Text", "Trading Card Games", "Fuckery", "Training"
]
cat = st.sidebar.radio("Select Category/Mode", categories, index=0)

feature_focus = None
fuckery_key_message = ""
if cat == "Fuckery":
    st.sidebar.warning("Which core feature do you want to stress-test?")
    feature_focus = st.sidebar.selectbox(
        "Choose primary focus:",
        ["Art", "Sound", "Video", "Text"],
        index=0
    )
    agent.set_mode(cat, feature_focus)
    key = agent.get_fuckery_encryption_key()
    if key:
        fuckery_key_message = f"**Fuckery Mode Encryption Key:** `{key}`"
        st.sidebar.info(fuckery_key_message)
else:
    agent.set_mode(cat)

descriptions = {
    "Art": "Prioritizes image and visual art tools and data.",
    "Sound": "Prioritizes audio/music analysis, generation, and plugins.",
    "Video": "Prioritizes video creation, editing, analysis.",
    "Text": "Prioritizes text generation, summarization, legal/web Q&A.",
    "Trading Card Games": "Optimizes for TCG/CCG data, deck analysis, and plugins.",
    "Fuckery": "Stress-testing! All files and content are encrypted in stealth mode.",
    "Training": "Focuses on data ingestion, analysis, and embedding; disables output generation."
}
st.sidebar.info(descriptions[cat])
st.markdown(fuckery_key_message)

st.header("RAE.IO Agent")
prompt = st.text_area("Enter your prompt:")

if st.button("Run Task") and prompt.strip():
    try:
        output = agent.run_task(cat.lower(), prompt, context={}, plugin=None)
        st.success(f"Task output: {output}")
    except Exception as e:
        st.error(f"Error: {e}")