# RAE.IO – Full Launch Instructions

These instructions will help you install, set up, and launch your RAE.IO application on Windows, macOS, Linux, or as a Dockerized web app.

---

## 1. **Download/Clone the Project**

- **From GitHub:**  
  - Click the green **Code** button and choose **Download ZIP** OR  
  - Use `git clone https://github.com/YOUR-USERNAME/raeio.git`  
- **Extract** the ZIP file to a directory of your choice if you downloaded it.

---

## 2. **Install Dependencies**

### **Windows**
1. Open the extracted folder in **File Explorer**.
2. Double click `install.bat`.
3. If prompted, allow the script to run as Administrator.
4. This will:
   - Check/install Python 3.10+
   - Install required Python packages
   - Install a suitable font
5. When you see "Installation complete," close the window.

### **macOS**
1. Open **Terminal**.
2. `cd` into your project directory.
3. Run `chmod +x install.command` to make the installer executable.
4. Run `./install.command`.
5. This will:
   - Install Homebrew (if needed)
   - Install Python 3, pip, dependencies, and font
6. Wait for "Installation complete."

### **Linux (Debian/Ubuntu/Fedora/Arch)**
1. Open **Terminal**.
2. `cd` into your project directory.
3. Run `chmod +x install.sh` to make the installer executable.
4. Run `./install.sh`.
5. Wait for "Installation complete."

### **Docker (All platforms)**
1. Make sure [Docker](https://www.docker.com/get-started/) is installed.
2. In Terminal (in your project folder), run:
   ```
   docker build -t raeio .
   docker run -p 8501:8501 -v $(pwd)/data:/app/data raeio
   ```
3. This will launch the app in a container and map persistent storage.

---

## 3. **Launching the Application**

### **Standard (Non-Docker)**
- Open Terminal/Command Prompt.
- Navigate (`cd`) to the folder where you installed/extracted RAE.IO.
- Run:
  ```
  streamlit run ui.py
  ```
- Wait for Streamlit to say it’s running (you’ll see a local URL, usually http://localhost:8501).

### **Docker**
- The app will be available at [http://localhost:8501](http://localhost:8501) as soon as the container finishes starting.
- If you set up Docker with a different port, adjust the URL accordingly.

---

## 4. **Using the Application**

- Go to [http://localhost:8501](http://localhost:8501) in your web browser.
- Use the **sidebar** to select a mode: Art, Sound, Video, Text, Trading Card Games, Fuckery, Training.
- When “Fuckery” mode is activated:
  - You’ll receive an **encryption key**. Copy and save this key immediately!
  - All data/files created in this mode will be ENCRYPTED and can only be accessed with this key.
- Each mode prioritizes relevant tools, plugins, and workflows.
- For more details, see the in-app **Help** or `HOW_TO_USE.md`.

---

## 5. **Troubleshooting**

- **Python not found:** [Download Python 3.10+](https://www.python.org/downloads/)
- **Missing dependencies:** Rerun the installer script for your OS.
- **Fonts don’t appear:** Some OSes may require a reboot after font installation.
- **Port in use:** Change the port in the `streamlit run ui.py` command with `--server.port=XXXX`.

---

## 6. **Upgrading/Customizing**

- To add your own plugins, place Python scripts in the `plugins` folder and reload from the sidebar.
- For advanced customization, see developer docs and source code comments.

---

## 7. **Uninstalling**

- Simply delete the extracted RAE.IO folder.
- To remove the font, delete it from your system’s font manager.
- If you used Docker, remove the image: `docker rmi raeio`

---

**For more help, see `HOW_TO_USE.md`, open an issue on GitHub, or ask for support!**