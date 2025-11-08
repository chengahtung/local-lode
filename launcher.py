import subprocess
import time
import sys
import os

# Path to your Chrome executable
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_SCRIPT = "rag_main.py"  # Your Streamlit script

# Start Streamlit
streamlit_proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", STREAMLIT_SCRIPT,"--server.headless", "true"])

# Wait a few seconds for Streamlit server to start
#time.sleep(3)

# Open Chrome in app mode (new instance)
chrome_proc = subprocess.Popen([CHROME_PATH, "--app=http://localhost:8501"])

