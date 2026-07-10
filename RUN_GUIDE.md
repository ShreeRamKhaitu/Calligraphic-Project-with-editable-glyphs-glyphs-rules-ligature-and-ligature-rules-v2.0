# Running the Ranjana Calligraphic AI Studio

## Quick Start

### Linux / Mac
```bash
bash start.sh
```

### Windows
Double-click `start.bat` **or** open Command Prompt in the project folder and run:
```cmd
start.bat
```

Then open your browser at: **http://localhost:8000**

---

## Manual Setup (First Time Only)

### Step 1 — Create a virtual environment

**Linux:**
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### Step 2 — Start the server

**Linux:**
```bash
.venv/bin/python3 api.py
```

**Windows:**
```cmd
.venv\Scripts\python.exe api.py
```

---

## Key Features
- **Glyph Studio**: Customize character scaling, offsets, and surgical cropping.
- **Monogram Generator**: Generate vertical stacks with automatic positional rules (First, Middle, Last).
- **Ligature Studio**: Build and fine-tune complex ligatures.
- **Word Builder**: Build words by drawing characters and render them vertically.

---

## Troubleshooting

| Problem | Linux fix | Windows fix |
|---------|-----------|-------------|
| Port 8000 in use | `fuser -k 8000/tcp` | `netstat -aon \| findstr :8000` then `taskkill /PID <pid> /F` |
| Missing packages | `.venv/bin/pip install -r requirements.txt` | `.venv\Scripts\pip install -r requirements.txt` |
| Font not found | Make sure `NithyaRanjanaDU-Regular.otf` is in the project folder | Same |
