from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, os, threading, csv, traceback, time, json
from concurrent.futures import ThreadPoolExecutor, as_completed

from database    import (create_database, insert_articles_batch,
                         search_articles, get_summary, export_to_csv, _get_conn)
from rule_engine import analyze_chunk
from chunker     import get_chunks

app = Flask(__name__)

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ── Shared state ─────────────────────────────────────────────
progress = {
    "total": 0, "completed": 0, "status": "idle", "logs": [],
    "sequential_time": None, "parallel_time": None, "speedup": None
}
uploaded_file_path = ""
raw_text           = ""
last_search_results = []


# ──────────────────────────────────────────────────────────────
#  PAGES
# ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search_page")
def search_page():
    return render_template("search.html")

@app.route("/results_page")
def results_page():
    return render_template("results.html")


# ──────────────────────────────────────────────────────────────
#  UPLOAD
# ──────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".txt", ".csv", ".json", ".jsonl", ".md", ".log", ".xml"}

@app.route("/upload", methods=["POST"])
def upload():
    global uploaded_file_path, raw_text

    file = request.files.get("file")
    text = request.form.get("text", "").strip()

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS and ext != "":
            # Still allow unknown extensions — chunker has fallback
            pass
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)
        uploaded_file_path = path
        raw_text           = ""

        # Check empty file
        if os.path.getsize(path) == 0:
            return jsonify({"warning": "File is empty — nothing to process."})

        return jsonify({"message": f"File '{file.filename}' uploaded successfully."})

    elif text:
        if not text:
            return jsonify({"error": "Text input is empty."})
        raw_text           = text
        uploaded_file_path = ""
        return jsonify({"message": "Text received successfully."})

    return jsonify({"error": "No input provided."})


# ──────────────────────────────────────────────────────────────
#  PROCESSING WORKER  (runs in ProcessPoolExecutor)
# ──────────────────────────────────────────────────────────────

def _process_chunk_worker(chunk_data: dict) -> dict:
    """Runs inside a worker thread."""
    import threading as _threading, time as _time
    start = _time.time()

    articles = []
    for line in chunk_data["text"].split("\n"):
        line = line.strip()
        if line:
            articles.append({"text": line, "analysis": analyze_chunk(line)})

    return {
        "chunk_id":        chunk_data["chunk_id"],
        "articles":        articles,
        "worker_pid":      _threading.current_thread().name,
        "processing_time": _time.time() - start
    }


# ──────────────────────────────────────────────────────────────
#  SEQUENTIAL PASS  (for timing comparison)
# ──────────────────────────────────────────────────────────────

def _run_sequential(chunks: list) -> float:
    start = time.time()
    for chunk in chunks:
        result = _process_chunk_worker(chunk)
        insert_articles_batch(result["articles"])
        progress["completed"] += 1
        progress["logs"].append(
            f"[Sequential] Chunk {result['chunk_id']} done in {result['processing_time']:.4f}s"
        )
    return time.time() - start





# ──────────────────────────────────────────────────────────────
#  PARALLEL PASS
# ──────────────────────────────────────────────────────────────

def _run_parallel(chunks: list, workers: int) -> float:
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_process_chunk_worker, c) for c in chunks]
        order = 1
        for future in as_completed(futures):
            result = future.result()
            insert_articles_batch(result["articles"])
            progress["completed"] += 1
            progress["logs"].append(
                f"[Parallel #{order}] Chunk {result['chunk_id']} | PID {result['worker_pid']} | {result['processing_time']:.4f}s"
            )
            order += 1
    return time.time() - start


# ──────────────────────────────────────────────────────────────
#  MAIN PROCESSING THREAD
# ──────────────────────────────────────────────────────────────

def process_file(workers: int, chunk_size: int):
    global raw_text, uploaded_file_path

    try:
        progress.update({
            "status": "running", "logs": [],
            "total": 0, "completed": 0,
            "sequential_time": None, "parallel_time": None, "speedup": None
        })

        create_database(reset=True)

        source = raw_text if raw_text else uploaded_file_path
        if not source:
            progress["logs"].append("⚠ No input provided.")
            progress["status"] = "error"
            return

        chunks = get_chunks(source, chunk_size)

        if not chunks:
            progress["logs"].append("⚠ No text chunks found (file may be empty or unsupported).")
            progress["status"] = "done"
            return

        # total = chunks × 2 (sequential + parallel)
        progress["total"]     = len(chunks) * 2
        progress["completed"] = 0

        progress["logs"].append(f"Total chunks: {len(chunks)} | Workers: {workers}")
        progress["logs"].append("── Phase 1: Sequential ────────────────")

        seq_time = _run_sequential(chunks)
        progress["sequential_time"] = round(seq_time, 4)
        progress["logs"].append(f"✔ Sequential done in {seq_time:.4f}s")

        # Reset DB for parallel pass (fresh results)
        create_database(reset=True)
        progress["logs"].append("── Phase 2: Parallel ──────────────────")

        par_time = _run_parallel(chunks, workers)
        progress["parallel_time"] = round(par_time, 4)
        speedup = seq_time / par_time if par_time > 0 else 0
        progress["speedup"] = round(speedup, 2)

        progress["logs"].append(f"✔ Parallel done in {par_time:.4f}s")
        progress["logs"].append(f"🚀 Speedup: {speedup:.2f}x")
        progress["status"] = "done"

    except Exception as e:
        traceback.print_exc()
        progress["status"] = "error"
        progress["logs"].append(f"ERROR: {e}")


# ──────────────────────────────────────────────────────────────
#  API ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.route("/start", methods=["POST"])
def start():
    data    = request.json or {}
    workers = int(data.get("workers", os.cpu_count()))
    chunk   = int(data.get("chunk",   100))
    threading.Thread(target=process_file, args=(workers, chunk), daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/status")
def status():
    return jsonify(progress)


@app.route("/timing")
def timing():
    return jsonify({
        "sequential_time": progress["sequential_time"],
        "parallel_time":   progress["parallel_time"],
        "speedup":         progress["speedup"]
    })


@app.route("/results")
def results():
    conn = _get_conn()
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM processed_articles")
    total = cur.fetchone()[0]

    cur.execute("SELECT AVG(sentiment_score) FROM processed_articles")
    avg = cur.fetchone()[0] or 0

    cur.execute("SELECT sentiment_label, COUNT(*) FROM processed_articles GROUP BY sentiment_label")
    sentiment = cur.fetchall()

    cur.execute("SELECT tags, COUNT(*) FROM processed_articles GROUP BY tags")
    themes = cur.fetchall()

    cur.execute("""
        SELECT text_chunk, keywords, sentiment_label, sentiment_score
        FROM processed_articles LIMIT 100
    """)
    rows = cur.fetchall()
    conn.close()

    return jsonify({
        "total":     total,
        "avg":       round(avg, 2),
        "sentiment": sentiment,
        "themes":    themes,
        "rows":      rows
    })


@app.route("/keywords")
def keywords():
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT keywords FROM processed_articles")
    rows = cur.fetchall()
    conn.close()

    kw_set = set()
    for r in rows:
        if r[0]:
            for k in r[0].split(","):
                k = k.strip()
                if k:
                    kw_set.add(k)

    return jsonify(sorted(kw_set)[:50])


# ─── Search ──────────────────────────────────────────────────

@app.route("/search_api")
def search():
    global last_search_results

    keyword   = request.args.get("keyword",   "")
    min_score = request.args.get("min_score", None)
    max_score = request.args.get("max_score", None)

    min_s = int(min_score) if min_score not in (None, "") else None
    max_s = int(max_score) if max_score not in (None, "") else None

    rows = search_articles(keyword, min_s, max_s)
    last_search_results = rows

    return jsonify({"count": len(rows), "data": rows})


# ─── Live single-sentence analysis (no DB) ───────────────────

@app.route("/live_analyze", methods=["POST"])
def live_analyze():
    text = (request.json or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided."})
    result = analyze_chunk(text)
    return jsonify(result)


# ─── Export ──────────────────────────────────────────────────

def _build_export(rows, filename, fmt):
    if fmt == "excel":
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Text Chunk", "Keywords", "Sentiment Label", "Sentiment Score"])
        for r in rows:
            ws.append(list(r))
        path = f"{filename}.xlsx"
        wb.save(path)
    else:
        path = f"{filename}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Text Chunk", "Keywords", "Sentiment Label", "Sentiment Score"])
            writer.writerows(rows)
    return path


# ═══════════════════════════════════════════════════════════════
#  EMAIL CONFIGURATION
# ═══════════════════════════════════════════════════════════════
SMTP_SENDER   = "vatsak03@gmail.com"   # ← your Gmail (already set)
SMTP_APP_PASS = "yjuq ofgc uuwo uvvk"  # ← paste 16-char App Password


@app.route("/send_email", methods=["POST"])
def send_email():
    """
    User enters only the recipient email address.
    Backend builds the same Excel file as Export Excel
    and sends it as an email attachment.
    """
    import smtplib
    from email.message import EmailMessage

    data = request.json or {}
    to   = data.get("email",  "").strip()
    src  = data.get("source", "results")

    # ── Validate ──────────────────────────────────────────────
    if not to or "@" not in to:
        return jsonify({"success": False,
                        "error": "Please enter a valid email address."})

    if SMTP_APP_PASS == "PASTE_APP_PASSWORD_HERE" or len(SMTP_APP_PASS) < 10:
        return jsonify({"success": False,
                        "error": (
                            "Email not set up yet. "
                            "Open app.py, find SMTP_APP_PASS and paste your "
                            "Gmail App Password there. "
                            "Go to myaccount.google.com → Security → "
                            "2-Step Verification → App Passwords to generate one."
                        )})

    # ── Fetch data (same as Export Excel) ─────────────────────
    if src == "search":
        rows = last_search_results
    else:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute(
            "SELECT text_chunk, keywords, sentiment_label, sentiment_score "
            "FROM processed_articles"
        )
        rows = cur.fetchall()
        conn.close()

    if not rows:
        return jsonify({"success": False,
                        "error": "No data to send. Process a file first."})

    # ── Build Excel (identical to Export Excel button) ─────────
    xlsx_path = _build_export(rows, "data/email_export", "excel")

    # ── Send via Gmail ─────────────────────────────────────────
    try:
        msg            = EmailMessage()
        msg["Subject"] = "SENTRIX — Your Analysis Results"
        msg["From"]    = SMTP_SENDER
        msg["To"]      = to
        body = "Hi," + chr(10) + chr(10) + "Please find your SENTRIX analysis results attached as an Excel file." + chr(10) + chr(10) + "Total records: " + str(len(rows)) + chr(10) + chr(10) + "Sent by SENTRIX Parallel Processing Engine." + chr(10)
        msg.set_content(body)

        with open(xlsx_path, "rb") as xf:
            msg.add_attachment(
                xf.read(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename="sentrix_results.xlsx"
            )

        # Remove spaces from app password in case user pasted with spaces
        clean_pass = SMTP_APP_PASS.replace(" ", "")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_SENDER, clean_pass)
            server.send_message(msg)

        return jsonify({"success": True})

    except smtplib.SMTPAuthenticationError:
        return jsonify({"success": False,
                        "error": (
                            "Gmail login failed. "
                            "Make sure SMTP_APP_PASS in app.py is a 16-character "
                            "Gmail App Password — NOT your regular Gmail password. "
                            "Generate one at: myaccount.google.com → Security → "
                            "2-Step Verification → App Passwords."
                        )})
    except smtplib.SMTPRecipientsRefused:
        return jsonify({"success": False,
                        "error": "Recipient email '" + to + "' was rejected. Please check the address."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/export_search")
def export_search():
    fmt      = request.args.get("type",     "csv")
    filename = request.args.get("filename", "search_results")
    path     = _build_export(last_search_results, filename, fmt)
    return send_file(path, as_attachment=True)


@app.route("/export_all")
def export_all():
    fmt  = request.args.get("type", "csv")
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT text_chunk, keywords, sentiment_label, sentiment_score FROM processed_articles")
    rows = cur.fetchall()
    conn.close()
    path = _build_export(rows, "results", fmt)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)   # use_reloader=False avoids double-spawning processes
