import tkinter as tk
from tkinter import ttk, messagebox
import yaml
import logging
from raeio_agent import RAEIOAgent

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
logger = logging.getLogger("RAEIO_GUI")
agent = RAEIOAgent(config, logger)

def run_task():
    mode = mode_var.get()
    prompt = prompt_entry.get()
    output = agent.run_task(mode.lower(), prompt, {}, plugin=None)
    messagebox.showinfo("Output", output)

root = tk.Tk()
root.title("RAE.IO Desktop")

mode_var = tk.StringVar()
mode_box = ttk.Combobox(root, textvariable=mode_var, values=["art", "sound", "video", "text", "tcg", "fuckery", "training", "browser"])
mode_box.pack()
prompt_entry = tk.Entry(root, width=40)
prompt_entry.pack()
run_btn = tk.Button(root, text="Run Task", command=run_task)
run_btn.pack()

root.mainloop()