# Project Setup

This project is developed on **Python 3.12** - download from Microsoft Store

This project uses Python and requires installing some external libraries before running.

This project is powered by Streamlit.

After setup, may use `run_app.bat` in main program folder.

## 1. Create and activate a virtual environment (recommended)

```bash
# Open command line in the folder
Right-click any blank space in the main folder, then "Open in Terminal"

# Create a virtual environment (Recommended) -- Skip all below if not needed
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\activate

# On Linux / macOS:
source venv/bin/activate
```

## 2. Install all required packages

```
pip install -r requirements.txt --verbose --progress-bar=on
```

## 3. Create .env file (API_KEY)

```
# Create .env file and fill up the content, may refer to .env_sample
```

## 4. Run the project

```
# if virtual environment activated
streamlit run rag_main.py
or
# if no need virtual environment (run command from main folder)
python -m streamlit run rag_main.py
```

The user interface should pop up as a browser. If not, use the link given in the cmd.

## 5. Upload knowledge in the 'kb' folder to consume

```
1. Place your notes/knowledge into 'kb' folder
2. Click on 'Ingest KB' from the user interface (left panel)
3. Wait for ingestion complete
```

`chroma_db` folder will be automatically created (stores embeddings of notes/knowledge)

**Tips**: Inclued the document name inside the text of the document [improves search]

## 6. Query using natural language

===========================================================

#### Quick commands:

###### Quick run from cmd (cmd in folder)

```
python -m streamlit run rag_main.py
```

###### Activate virtual environment (If using virtual environment)

```
# On Windows (PowerShell):
.\venv\Scripts\activate

# On Linux / macOS:
source venv/bin/activate
```
