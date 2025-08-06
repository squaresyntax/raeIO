import streamlit as st
from raeio_agent import RAEIOAgent
import yaml
import logging
from model_trainer import train_model

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

logger = logging.getLogger("RAEIO_UI")
agent = RAEIOAgent(config, logger)

st.title("RAE.IO Agent Interface")

mode = st.selectbox(
    "Mode",
    ["Art", "Sound", "Video", "Text", "Trading Card Games", "Fuckery", "Training"],
)

if mode == "Training":
    model = st.selectbox("Model", ["sd", "llama"])
    dataset = st.text_input("Path to local dataset")
    output_dir = st.text_input("Checkpoint output directory", value="checkpoints")
    if st.button("Start Training"):
        if dataset.strip():
            result = train_model(model, dataset, output_dir)
            st.success(
                f"Training complete. Checkpoint saved to {result['checkpoint']}"
            )
        else:
            st.error("Please provide a dataset path.")
else:
    prompt_type = st.selectbox("Prompt Type", ["Text", "Image", "Video"])
    prompt = st.text_area("Enter your prompt here:")
    if st.button("Run Task") and prompt.strip():
        context = {}
        plugin = None
        try:
            output = agent.run_task(prompt_type.lower(), prompt, context, plugin=plugin)
            st.success(f"Task output: {output}")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.markdown("See [HOW_TO_USE.md](HOW_TO_USE.md) for more info.")