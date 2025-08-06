import tkinter as tk
from tkinter import ttk, messagebox
import yaml
import logging
from raeio_agent import RAEIOAgent
from model_registry import all_features

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
logger = logging.getLogger("RAEIO_GUI")
agent = RAEIOAgent(config, logger)

def run_task():
    feature = feature_var.get()
    prompt = prompt_entry.get()
    output = agent.run_task(feature, prompt, {}, plugin=None)
    messagebox.showinfo("Output", output)

root = tk.Tk()
root.title("RAE.IO Desktop")

features = all_features()
feature_var = tk.StringVar(value=features[0])
feature_box = ttk.Combobox(root, textvariable=feature_var, values=features)
feature_box.pack()
prompt_entry = tk.Entry(root, width=40)
prompt_entry.pack()
run_btn = tk.Button(root, text="Run Task", command=run_task)
run_btn.pack()

root.mainloop()