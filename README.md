# Local Lode 📝 — Note Search Tool
**Never lose track of your notes again.**  
A **local-first** note search tool that helps you rediscover your knowledge instantly.  
LocalLode helps you quickly search, organize, and retrieve your personal notes on your device.


### **Ever lost track of your own notes?**  
You know you wrote something important… but where did you save it?  
Local Lode is here to end that frustration and help you **know what you already know**.
> Stop hunting for lost notes.
> Keep track of your ideas effortlessly. 🚀
---

## ❔ Why I Built This

- As a software developer, **understanding/analyzing a codebase can be time-consuming**. After studying complex code, I often take notes to document its behavior and workflow to avoid reanalyzing.
- I often **forget where I store notes** across multiple folders and drives.  
- **Digging through them wastes time**, causes duplicate notes, and interrupts my workflow.  

Local Lode was created to solve this problem — a lightweight tool that lets you **locate your local notes instantly**.  
It also helps you **rediscover information you’ve already captured**, so you can work smarter, not harder.

---

## What It Does

- 🔍 Search any local note across multiple folders  
- ⚡ Fast and lightweight, runs directly on your computer  
- 🛠️ Minimal setup with no complicated dependencies  
- 💡 Helps prevent duplicate work by showing you what you’ve already noted  
- Keeps your workflow organized and efficient  

---

## 📑 Table of Contents

- [❔ Why I Built This](#why-i-built-this)
- [What It Does](#what-it-does)
- [🚀 Getting Started](#getting-started)
  - [🧩 1. Create and Activate a Virtual Environment (Recommended)](#1-create-and-activate-a-virtual-environment-recommended)
  - [📦 2. Install Required Packages](#2-install-required-packages)
  - [🔑 3. Setup / Create `.env` File (API_KEY) -- optional](#3-setup--create-env-file-api_key---optional)
  - [▶️ 4. Run the Project](#4-run-the-project)
    - [💡 4.1 Alternative Run Method](#41-alternative-run-method)
- [📚 5. Upload Knowledge Base (‘kb’ Folder)](#5-upload-knowledge-base-kb-folder)
- [🔍 6. Query Using Natural Language](#6-query-using-natural-language)
- [⚡ Quick Commands](#quick-commands)
- [🗑️ Reset Tip](#reset-tip)
- [License](#license)
- [Support the Project 💖](#support-the-project-)

---

# 🚀 **Getting Started**

This project uses **🐍 Python 3.12.10**.  
- Recommended: Install Python from [python.org](https://www.python.org/downloads/).  
- Alternative: Microsoft Store version (⚠️ may cause PATH issues on some systems).

It uses **FastAPI** for the backend and a modern **Vanilla JavaScript** frontend.
> When launched, Local Lode starts a local server and opens a clean, responsive dashboard where you can search your notes, ingest new files, and view retrieved content instantly.

You can launch the app using **`local-lode.bat`** in the main program folder for a one-click experience.

---

## 🧩 **1. Create and Activate a Virtual Environment (Recommended)**

```Markdown
# 💻 Open Command Prompt in Project Folder

1. **Open Windows File Explorer** and navigate to the folder where you saved **Local Lode**.

2. **Click the address bar at the top** (where the folder path is shown).

3. Type `cmd` and press Enter.
> This opens a Command Prompt with the current folder set as the working directory.

# 🐍 Create a virtual environment (Recommended)
python -m venv venv

# ⚡ Activate virtual environment
- On Windows:
.\venv\Scripts\activate

- On Linux / macOS:
source venv/bin/activate
```

> 💡 *You may skip this step if you prefer using your global system Python environment.*

---

## 📦 **2. Install Required Packages**

```bash
pip install -r requirements.txt --verbose --progress-bar=on
```

---

## 🔑 **3. Setup / Create `.env` File (API_KEY)** -- optional

> !!! This key is required if you want to use LLM-based query generation (Uses `Gemini` for now)

```Markdown
🧾 Create a .env file in the main folder
Fill in your API key — you can refer to the sample provided in `.env_sample`
```

---

## ▶️ **4. Run the Project**

Simply **double-click** the unified launcher in the main folder:

- **➡️ `local-lode.bat`** — Automatically starts the backend and opens the app in your browser.

### 💡 **4.1 Terminal Run Method**

If you prefer using the terminal, run the following command from the project root:

```bash
# Start the unified launcher
python launcher_new.py
```

### �️ **4.2 Legacy Version (Streamlit)**

The older Streamlit-based version is still available but no longer the primary focus:

- **➡️ `local-lode(browser).bat`** — Open Streamlit version in active browser tab  
- **➡️ `local-lode(app).bat`** — Open Streamlit version as separate Chrome app

```bash
# To run Streamlit manually:
streamlit run rag_main.py
```

---

## 📚 **5. Upload Knowledge Base (‘kb’ Folder)**

1. 🗂️ Place your notes or documents into the **`kb/`** folder.
2. ⚙️ From the application sidebar, click **“Ingest KB”**.
3. ⏳ Wait until the ingestion process completes (indicated by a success message).

A **`chroma_db/`** folder will be automatically created — it stores embeddings of your notes.

> 💬 **Tip:** Include the document name inside your text to **improve search accuracy**.

---

## 🔍 **6. Query Using Natural Language**

Once your knowledge is ingested, simply type a natural-language question.
The system retrieves, reranks, and optionally uses an **LLM** to generate answers.

---

## ⚡ **Quick Commands**

### ▶️ **Run from Command Line**

```bash
# Run the new unified launcher (Primary)
python launcher_new.py

# Run the legacy Streamlit version
python -m streamlit run rag_main.py
```

### 🧠 **Activate Virtual Environment**

```bash
# On Windows (PowerShell):
.\venv\Scripts\activate

# On Linux / macOS:
source venv/bin/activate
```

---

### 🗑️ **Reset Tip**

> To reset the database, delete all contents in the **`chroma_db/`** folder.

---

## **License**

This project is licensed under the **MIT License**.

For details, see the [LICENSE](LICENSE) file.

---

## Support the Project 💖

- If you enjoy LocalLode, you can support development via [donations](https://buymeacoffee.com/chengahtung).  
- In the future, LocalLode may offer a **paid Pro version** with extra features and convenience tools.  
- Supporting now helps keep the project alive and evolving.

### Ways to Support

* **Buy Me a Coffee**: [☕ Buy Me a Coffee](https://buymeacoffee.com/chengahtung)
* **GitHub Sponsors**: [💖 Sponsor on GitHub](https://github.com/sponsors/chengahtung)

[![Sponsor](https://img.shields.io/badge/Sponsor-☕-ff69b4)](https://buymeacoffee.com/chengahtung)

---



