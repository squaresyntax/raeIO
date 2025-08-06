import streamlit as st
from raeio_agent import RAEIOAgent
import yaml
import logging

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

logger = logging.getLogger("RAEIO_UI")
agent = RAEIOAgent(config, logger)

st.title("RAE.IO Agent Interface")

mode = st.selectbox("Mode", ["Art", "Sound", "Video", "Text", "Trading Card Games", "Fuckery", "Training"])
prompt_type = st.selectbox("Prompt Type", ["Text", "Image", "Video"])

prompt = st.text_area("Enter your prompt here:")

run_task = st.button("Run Task")

if run_task and prompt.strip():
    context = {}
    plugin = None
    # Example: For browser automation, you might add URL/actions to context
    try:
        output = agent.run_task(prompt_type.lower(), prompt, context, plugin=plugin)
        st.success(f"Task output: {output}")
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.markdown("See [HOW_TO_USE.md](HOW_TO_USE.md) for more info.")