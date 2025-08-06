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

if st.button("Run Task"):
    if prompt.strip():
        context = {}
        plugin = None
        # Example: For browser automation, you might add URL/actions to context
        try:
            output = agent.run_task(prompt_type.lower(), prompt, context, plugin=plugin)
            st.success(f"Task output: {output}")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.header("Model Training")

train_model = st.selectbox("Model to train", ["LLaMA", "Stable Diffusion"], key="train_model")
dataset_path = st.text_input("Dataset path")
if st.button("Start Training"):
    try:
        if train_model == "LLaMA":
            from trainers.llama_trainer import train_model as train_llama
            ckpt = train_llama(dataset_path)
        else:
            from trainers.sd_trainer import train_model as train_sd
            ckpt = train_sd(dataset_path)
        st.success(f"Checkpoint saved to {ckpt}")
    except Exception as e:
        st.error(f"Training failed: {e}")

st.subheader("Restore Checkpoint")
restore_model = st.selectbox("Model to restore", ["LLaMA", "Stable Diffusion"], key="restore_model")
if restore_model == "LLaMA":
    from trainers.llama_trainer import list_checkpoints, restore_checkpoint
else:
    from trainers.sd_trainer import list_checkpoints, restore_checkpoint
ckpts = list_checkpoints()
checkpoint = st.selectbox("Available checkpoints", ckpts)
if st.button("Restore"):
    try:
        metadata = restore_checkpoint(checkpoint)
        st.success(f"Restored checkpoint: {metadata}")
    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.markdown("See [HOW_TO_USE.md](HOW_TO_USE.md) for more info.")
