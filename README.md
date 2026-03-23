# SENTRIX — Parallel Text Handling Processor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00f5c4?style=for-the-badge)
![Internship](https://img.shields.io/badge/Infosys%20Springboard-6.0-FF6200?style=for-the-badge)

**A Scalable, Parallel Text Processing System built for the Infosys Springboard Internship 6.0**

*Processes any text file at machine speed — chunks, scores sentiment, detects themes, visualizes results — simultaneously across CPU cores.*

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [API Reference](#-api-reference)

</div>

---

## 📌 Project Overview

**SENTRIX** is a full-stack parallel text processing engine developed as part of the **Infosys Springboard Internship 6.0** under the project title **"Python Parallel Text Handling Processor"**.

The system is designed to efficiently process large volumes of text data using Python's parallel execution capabilities without relying on heavy AI/ML frameworks. It combines multi-threading, rule-based sentiment analysis, structured database storage, an interactive web UI, and automated reporting making it accessible to language researchers, data analysts, NLP beginners, and small organizations.

### What Makes It Different

- ✅ **No ML dependencies** : Pure rule-based engine, fully transparent and modifiable
- ✅ **True parallel execution** : `ThreadPoolExecutor` processes multiple chunks simultaneously
- ✅ **Any file format** : `.txt`, `.csv`, `.json`, `.jsonl`, `.xml`, `.md`, `.log`
- ✅ **Any file size** : Streaming chunker prevents memory overflow
- ✅ **Real-time monitoring** : Live chunk logs, progress bar, execution timing
- ✅ **Professional UI** : Dark cyberpunk theme with animated charts and page transitions

---

## ✨ Features

### Core Processing
| Feature | Description |
|---|---|
| **Parallel Chunking** | Splits files into line/row-based chunks processed simultaneously |
| **Sequential vs Parallel Timing** | Measures and compares both execution modes |
| **Speedup Calculation** | Shows how many times faster parallel is vs sequential |
| **Multi-format Support** | Auto-detects `.txt`, `.csv`, `.json`, `.jsonl`, `.xml`, `.md`, `.log` |
| **Any File Size** | Handles small snippets to 50,000+ row CSV files |
| **Raw Text Input** | Paste text directly without uploading a file |

### Sentiment Analysis Engine
| Feature | Description |
|---|---|
| **Rule-Based Scoring** | No ML model needed — pure word-list + logic approach |
| **5-Level Labels** | Strongly Positive → Positive → Neutral → Negative → Strongly Negative |
| **Repetition Counting** | `good good good` scores `+3`, not `+1` |
| **Negation Handling** | `not good → -1`, `not bad → 0` (absence of bad ≠ good) |
| **Contrast Conjunctions** | Splits at `but`, `yet`, `however`, `although` — balances both sides |
| **Prefix Morphology** | `unhappy → -1`, `unsuccessful → -1` (root-confirmed only) |
| **No Suffix Guessing** | `sadness → -1` (in list), `kindness → 0` (not guessed) |
| **Theme Detection** | 10 categories: Economy, Politics, Tech, Sports, Health, World, Environment, Education, Business, Crime |

### Scoring Thresholds
```
score == 0    →  Neutral
score >= 1    →  Positive
score >= 5    →  Strongly Positive
score <= -1   →  Negative
score <= -5   →  Strongly Negative
```

### Web Interface
| Page | Features |
|---|---|
| **Upload** | Drag & drop file upload, paste text, workers config, rows/chunk config, live processing log, per-chunk timing chart, sequential vs parallel timing |
| **Results** | Animated stat cards, doughnut chart, bar chart, polar chart, data type auto-detection, results table, export to CSV/Excel, email results |
| **Search** | Keyword / sentence / both search modes, score range filter, keyword suggestions, highlighted results table, export filtered results, email search results |

### Export & Reporting
- Export results as **CSV** or **Excel (.xlsx)**
- Export search results as **CSV** or **Excel**
- **Email results** as Excel attachment to any email address
- Per-chunk execution time chart in the sidebar

---

## 🖥 Demo

### Upload Page
```
📂 Drop any file → Set workers & rows/chunk → ▶ Start Processing
→ Watch live parallel chunk logs in sidebar
→ See Sequential vs Parallel execution times
→ Per-chunk timing bar chart auto-generates
```

### Results Page
```
📊 Auto-detected data type (News / Sports / Tech / etc.)
→ Total chunks, Avg sentiment score, Positive/Negative counts
→ 3 animated charts: Sentiment Distribution, Theme Frequency, Score Distribution
→ Scrollable results table with sentiment pills
→ Export CSV / Excel / Email
```

### Search Page
```
🔍 Type keyword or phrase → Click Search
→ Keyword suggestions auto-loaded from processed data
→ Filter by Min/Max sentiment score
→ Results table with keyword highlighting
→ Export / Email filtered results
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Step 1 — Clone the repository
```bash
git clone https://github.com/yourusername/sentrix.git
cd sentrix
```

### Step 2 — Install dependencies
```bash
pip install flask openpyxl
```

### Step 3 — Run the application
```bash
python app.py
```

### Step 4 — Open in browser
```
http://localhost:5000
```

> The `data/` folder is created automatically on first run. No database setup needed.

---

## 📁 Project Structure

```
Project/
│
├── app.py                  ← Flask server — routes, processing, export, email
├── chunker.py              ← Universal file chunker (line/row based)
├── rule_engine.py          ← Sentiment analysis engine (rule-based)
├── database.py             ← SQLite storage layer (WAL mode, thread-safe)
│
├── data/                   ← Auto-created at runtime
│   ├── text_processing.db  ← SQLite database
│   ├── email_export.xlsx   ← Temp file for email
│   ├── results.csv/xlsx    ← Export downloads
│   └── search_results.*    ← Search export downloads
│
├── templates/
│   ├── index.html          ← Upload & processing page
│   ├── results.html        ← Analytics dashboard
│   └── search.html         ← Search & filter page
│
└── static/
    ├── style.css           ← All styles for all 3 pages
    └── script.js           ← All JavaScript for all 3 pages
```

---

## 📖 Usage

### 1. Processing a File

1. Open `http://localhost:5000`
2. Drag & drop a file onto the upload zone **or** paste text in the text box
3. Set **Workers** (number of parallel threads, e.g. `4`)
4. Set **Rows / Lines per Chunk** (e.g. `500` for a large CSV)
5. Click **▶ Start Processing**
6. Watch the live log in the sidebar — each parallel chunk appears as it completes
7. After processing, the **Execution Times** panel shows Sequential vs Parallel timing
8. Click **📊 View Full Analytics & Results**

### 2. Viewing Results

1. Navigate to **Results** page
2. View animated stat cards, charts, and the full data table
3. Use **Export CSV** or **Export Excel** to download results

### 3. Searching

1. Navigate to **Search** page
2. Choose search mode: **Keyword**, **Sentence/Phrase**, or **Both**
3. Type a keyword — suggestions appear automatically from your processed data
4. Optionally filter by **Min Score** / **Max Score**
5. Press **Search** — results appear with keywords highlighted in teal
6. Export filtered results as CSV or Excel

### 4. Email Results

1. Process a file or run a search
2. In the email section, enter any recipient email address
3. Click **📤 Send** — the same Excel file as Export Excel is sent as an attachment

> **Setup required (one time):** Open `app.py` and set `SMTP_SENDER` and `SMTP_APP_PASS` at the top. See [Email Configuration](#-email-configuration).

### 5. Recommended Chunk Sizes

| File Type | File Size | Recommended Rows/Chunk |
|---|---|---|
| Small `.txt` | < 1MB | `50` |
| Medium `.csv` | 1–10MB | `200` |
| Large `.csv` | 10–50MB | `500` |
| Very Large `.csv` | 50k+ rows | `1000` |

---

## 🏗 Architecture

```
User (Browser)
      ↓
  Web UI  (index.html / results.html / search.html)
      ↓
  Flask API  (app.py)
      ↓
  ┌─────────────────────────────────────────┐
  │           Processing Pipeline           │
  │                                         │
  │  1. Chunker (chunker.py)                │
  │     → Reads file, splits into chunks    │
  │     → Line/row based for all formats    │
  │                                         │
  │  2. Sequential Pass                     │
  │     → Processes chunks one by one       │
  │     → Records total time                │
  │                                         │
  │  3. Parallel Pass (ThreadPoolExecutor)  │
  │     → Processes chunks simultaneously  │
  │     → Records total time + speedup     │
  │                                         │
  │  4. Rule Engine (rule_engine.py)        │
  │     → Scores sentiment per line         │
  │     → Detects themes                   │
  │                                         │
  │  5. Database (database.py)              │
  │     → SQLite WAL mode (thread-safe)    │
  │     → Batch inserts                    │
  └─────────────────────────────────────────┘
      ↓
  Results / Search / Export / Email
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | Flask routes, upload handling, threading, export, email |
| `chunker.py` | Auto-detects file format, splits into line/row chunks, handles encoding |
| `rule_engine.py` | Tokenizes text, scores sentiment, detects themes, handles negation & contrast |
| `database.py` | Creates SQLite DB with indexes, batch inserts, search queries, WAL mode |

### Parallel Execution Model

```
File Input
    ↓
[Chunker] → Chunk 1, Chunk 2, Chunk 3 ... Chunk N
                ↓         ↓         ↓
           Thread-1   Thread-2   Thread-3   (ThreadPoolExecutor)
                ↓         ↓         ↓
           Analyze    Analyze    Analyze    (rule_engine per line)
                ↓         ↓         ↓
           DB Write   DB Write   DB Write   (SQLite WAL — concurrent safe)
                ↓
          Results aggregated → UI
```

---

## 🔧 Configuration

### Workers & Chunk Size

Set in the UI before processing:

| Setting | What it controls | Recommended |
|---|---|---|
| **Workers** | Number of parallel threads | 4–8 (match your CPU cores) |
| **Rows/Lines per Chunk** | How many rows each thread processes | 100–1000 depending on file size |

### Email Configuration

Open `app.py` and update these two lines near the top:

```python
SMTP_SENDER   = "your_gmail@gmail.com"   # Your Gmail address
SMTP_APP_PASS = "abcdefghijklmnop"       # 16-char Gmail App Password
```

**How to generate a Gmail App Password:**
1. Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already on
3. Search **"App Passwords"** in the search bar
4. Select app: **Mail** → device: **Windows Computer** → click **Generate**
5. Copy the 16-character password and paste into `SMTP_APP_PASS`

> Your regular Gmail password will **not** work — you must use an App Password.

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Upload page |
| `/results_page` | GET | Results/analytics page |
| `/search_page` | GET | Search page |
| `/upload` | POST | Upload file or receive raw text |
| `/start` | POST | Start processing `{ workers, chunk }` |
| `/status` | GET | Poll processing progress and logs |
| `/timing` | GET | Get sequential/parallel times and speedup |
| `/results` | GET | Fetch aggregated results for dashboard |
| `/keywords` | GET | Fetch detected keywords for search suggestions |
| `/search_api` | GET | Search with `?keyword=&min_score=&max_score=` |
| `/live_analyze` | POST | Instant single-sentence analysis (no DB) |
| `/export_all` | GET | Download all results `?type=csv` or `?type=excel` |
| `/export_search` | GET | Download search results `?type=csv` or `?type=excel` |
| `/send_email` | POST | Email results `{ email, source }` |

---

## 📊 Sentiment Engine Details

### Word Lists
The engine uses explicit curated word lists — no suffix guessing:

- **~200 Positive words** — quality, emotions, success, growth, finance, innovation, service
- **~200 Negative words** — failure, conflict, harm, economic crisis, health, weakness
- **10 Theme categories** — Economy, Politics, Technology, Sports, Health, World, Environment, Education, Business, Crime

### Negation Logic
```
"not good"      → score -1   (negated positive = negative)
"not bad"       → score  0   (negated negative = neutral, not positive)
"never win"     → score -1   (negated positive)
"not terrible"  → score  0   (negated negative = neutral)
```

### Contrast Conjunction Logic
```
"productive yet took longer"
  → clause 1: "productive" = +1
  → clause 2: "longer"     = -1
  → total: 0 → Neutral ✓

"delicious but slow service"
  → clause 1: "delicious" = +1
  → clause 2: "slow"      = -1
  → total: 0 → Neutral ✓
```

### Prefix Morphology
```
"unhappy"       → un + happy (in positive list)  → -1
"unsuccessful"  → un + successful (in list)      → -1
"disorganized"  → dis + organized (in list)      → -1
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 2.x |
| **Parallel Processing** | `concurrent.futures.ThreadPoolExecutor` |
| **Database** | SQLite3 with WAL mode (Write-Ahead Logging) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Charts** | Chart.js 4.4.1 |
| **Fonts** | Syne (headings), Space Mono (body) |
| **Export** | openpyxl (Excel), csv (CSV) |
| **Email** | smtplib + EmailMessage (Gmail SMTP) |
| **File Parsing** | csv, json, re (XML/text) |

---

## 📧 Email Configuration

```python
# In app.py — set these once:
SMTP_SENDER   = "your_gmail@gmail.com"
SMTP_APP_PASS = "your_16_char_app_password"
```

After configuration, users simply enter any recipient email address in the UI and click Send. The same Excel file that the **Export Excel** button downloads is automatically sent as an email attachment.

---

## 🔒 Security Notes

- Gmail App Passwords are separate from your main Gmail password
- The App Password only grants access to send mail — not your full account
- For production deployment, store credentials in environment variables instead of hardcoding
- SQLite WAL mode ensures thread-safe concurrent writes during parallel processing
- Input sanitization is applied on all file uploads and search queries

---

## 🧪 Testing the Sentiment Engine

```python
from rule_engine import analyze_chunk

# Threshold tests
analyze_chunk("good")                    # score=+1  → Positive
analyze_chunk("good good good good good")# score=+5  → Strongly Positive
analyze_chunk("bad")                     # score=-1  → Negative
analyze_chunk("bad bad bad bad bad")     # score=-5  → Strongly Negative
analyze_chunk("the cat sat on the mat")  # score=0   → Neutral

# Contrast sentence tests
analyze_chunk("productive yet took longer than expected")  # score=0 → Neutral
analyze_chunk("delicious but the service was slow")        # score=0 → Neutral

# Negation tests
analyze_chunk("not good")   # score=-1 → Negative
analyze_chunk("not bad")    # score=0  → Neutral

# Suffix trap tests
analyze_chunk("sadness")    # score=-1 → Negative  (NOT positive)
analyze_chunk("kindness")   # score=0  → Neutral   (not guessed)
analyze_chunk("happiness")  # score=+1 → Positive
```

---

## 📝 Supported File Formats

| Format | Extension | Chunking Strategy |
|---|---|---|
| Plain Text | `.txt`, `.md`, `.log` | Each non-empty line = 1 unit |
| CSV | `.csv` | Each data row = 1 unit, header skipped |
| JSON | `.json` | Flattened to `key: value` lines |
| JSON Lines | `.jsonl` | Each JSON object = 1 line |
| XML | `.xml` | Tags stripped, remaining text lines used |
| Raw Text | — | Pasted directly in UI, line-split |

All formats handle:
- UTF-8, Latin-1, CP1252 encodings (auto-detected)
- Windows `\r\n` and Unix `\n` line endings
- Empty files (returns clear warning)

---

## 🤝 Contributing

This project was developed for the **Infosys Springboard Internship 6.0**. Contributions, suggestions, and improvements are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 👨‍💻 Author

**Vatsa** — Infosys Springboard Intern 6.0
- Project: *Python Parallel Text Handling Processor*
- System: **SENTRIX** — Parallel Text Intelligence Engine
- Email: vatsak03@gmail.com

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgements

- **Infosys Springboard** — for providing the internship platform and project guidance
- **Flask** — lightweight Python web framework
- **Chart.js** — beautiful animated charts
- **SQLite** — embedded database with WAL concurrency support
- **openpyxl** — Excel file generation

---

<div align="center">

**Built with ❤️ for Infosys Springboard Internship 6.0**

*SENTRIX — Process Any Text At Machine Speed*

</div>
