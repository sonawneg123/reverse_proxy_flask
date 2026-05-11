from flask import Flask, request, jsonify, render_template_string
import datetime
import platform
import sys
import os

app = Flask(__name__)

# ─────────────────────────────────────────────
#  Embedded HTML / CSS / JS  (single-file app)
# ─────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Server 1 · Flask API</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet"/>
  <style>
    /* ── Reset & variables ─────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #09090f;
      --surface:   #12121e;
      --border:    #1e1e32;
      --accent:    #00ffe7;
      --accent2:   #7b61ff;
      --danger:    #ff4d6d;
      --text:      #e0e0f0;
      --muted:     #5a5a7a;
      --mono:      'JetBrains Mono', monospace;
      --sans:      'Syne', sans-serif;
      --radius:    10px;
      --glow:      0 0 18px rgba(0,255,231,.25);
    }

    html { scroll-behavior: smooth; }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* ── Animated background grid ──────────── */
    body::before {
      content: '';
      position: fixed; inset: 0;
      background-image:
        linear-gradient(rgba(0,255,231,.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,231,.04) 1px, transparent 1px);
      background-size: 40px 40px;
      animation: gridDrift 20s linear infinite;
      pointer-events: none;
      z-index: 0;
    }
    @keyframes gridDrift { from { background-position: 0 0; } to { background-position: 40px 40px; } }

    /* ── Layout ────────────────────────────── */
    .wrapper {
      position: relative; z-index: 1;
      max-width: 900px;
      margin: 0 auto;
      padding: 48px 24px 80px;
    }

    /* ── Header ────────────────────────────── */
    header { margin-bottom: 48px; }

    .badge {
      display: inline-flex; align-items: center; gap: 8px;
      font-family: var(--mono); font-size: 11px; letter-spacing: .12em;
      color: var(--accent); text-transform: uppercase;
      border: 1px solid var(--accent); border-radius: 4px;
      padding: 4px 10px; margin-bottom: 18px;
    }
    .badge::before {
      content: ''; width: 7px; height: 7px;
      background: var(--accent); border-radius: 50%;
      animation: blink 1.4s ease-in-out infinite;
    }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }

    h1 {
      font-size: clamp(2rem, 5vw, 3.2rem);
      font-weight: 800; line-height: 1.08;
      letter-spacing: -.02em;
    }
    h1 span { color: var(--accent); }

    .subtitle {
      margin-top: 12px;
      font-family: var(--mono); font-size: 13px;
      color: var(--muted); letter-spacing: .04em;
    }

    /* ── Cards ─────────────────────────────── */
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 28px;
      margin-bottom: 24px;
      transition: border-color .2s;
    }
    .card:hover { border-color: var(--accent2); }

    .card-title {
      font-family: var(--mono); font-size: 11px;
      letter-spacing: .14em; text-transform: uppercase;
      color: var(--accent2); margin-bottom: 18px;
      display: flex; align-items: center; gap: 8px;
    }
    .card-title::before {
      content: ''; display: block;
      width: 20px; height: 1px; background: var(--accent2);
    }

    /* ── Endpoint pills ─────────────────────── */
    .endpoints { display: flex; flex-wrap: wrap; gap: 10px; }

    .ep-pill {
      display: flex; align-items: center; gap: 10px;
      background: rgba(0,0,0,.35);
      border: 1px solid var(--border);
      border-radius: 6px; padding: 9px 14px;
      cursor: pointer; transition: all .18s;
      font-family: var(--mono); font-size: 12px;
      user-select: none;
    }
    .ep-pill:hover { border-color: var(--accent); box-shadow: var(--glow); }
    .ep-pill.active { border-color: var(--accent); background: rgba(0,255,231,.06); }

    .method {
      font-weight: 700; font-size: 10px; letter-spacing: .08em;
      padding: 2px 6px; border-radius: 3px;
    }
    .get  { background: rgba(0,255,231,.15); color: var(--accent); }
    .post { background: rgba(123,97,255,.2); color: var(--accent2); }

    /* ── Request builder ────────────────────── */
    .req-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }

    input[type="text"], textarea, select {
      background: rgba(0,0,0,.4);
      border: 1px solid var(--border);
      border-radius: 6px; color: var(--text);
      font-family: var(--mono); font-size: 13px;
      padding: 10px 14px;
      transition: border-color .18s, box-shadow .18s;
      outline: none;
    }
    input[type="text"]:focus, textarea:focus, select:focus {
      border-color: var(--accent); box-shadow: var(--glow);
    }
    input[type="text"].url-input { flex: 1; min-width: 200px; }
    textarea { width: 100%; min-height: 90px; resize: vertical; margin-top: 12px; }

    /* ── Button ─────────────────────────────── */
    .btn {
      font-family: var(--mono); font-size: 13px; font-weight: 600;
      letter-spacing: .06em; text-transform: uppercase;
      padding: 11px 22px; border: none; border-radius: 6px;
      cursor: pointer; transition: all .18s;
      position: relative; overflow: hidden;
    }
    .btn-primary {
      background: var(--accent); color: #000;
    }
    .btn-primary:hover {
      box-shadow: 0 0 26px rgba(0,255,231,.5);
      transform: translateY(-1px);
    }
    .btn-primary:active { transform: translateY(0); }
    .btn-primary:disabled { opacity: .45; cursor: not-allowed; transform: none; }

    .btn-ghost {
      background: transparent; color: var(--muted);
      border: 1px solid var(--border);
    }
    .btn-ghost:hover { border-color: var(--muted); color: var(--text); }

    /* ── Response area ──────────────────────── */
    .response-header {
      display: flex; align-items: center;
      justify-content: space-between; margin-bottom: 12px;
    }
    .status-badge {
      font-family: var(--mono); font-size: 12px;
      padding: 4px 10px; border-radius: 4px; font-weight: 700;
      transition: all .3s;
    }
    .status-ok   { background: rgba(0,255,100,.15); color: #00ff64; border: 1px solid rgba(0,255,100,.3); }
    .status-err  { background: rgba(255,77,109,.15); color: var(--danger); border: 1px solid rgba(255,77,109,.3); }
    .status-idle { background: rgba(255,255,255,.05); color: var(--muted); border: 1px solid var(--border); }

    .response-time {
      font-family: var(--mono); font-size: 11px; color: var(--muted);
    }

    pre {
      background: rgba(0,0,0,.5);
      border: 1px solid var(--border);
      border-radius: 8px; padding: 18px;
      font-family: var(--mono); font-size: 12.5px;
      line-height: 1.7; overflow-x: auto;
      color: var(--text); min-height: 120px;
      white-space: pre-wrap; word-break: break-word;
    }

    /* ── Server info grid ───────────────────── */
    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }
    .info-item { display: flex; flex-direction: column; gap: 5px; }
    .info-label {
      font-family: var(--mono); font-size: 10px;
      letter-spacing: .12em; text-transform: uppercase; color: var(--muted);
    }
    .info-value {
      font-family: var(--mono); font-size: 13px; color: var(--accent);
    }

    /* ── History ────────────────────────────── */
    .history-list { display: flex; flex-direction: column; gap: 8px; max-height: 260px; overflow-y: auto; }
    .history-item {
      display: flex; align-items: center; gap: 10px;
      font-family: var(--mono); font-size: 11px;
      padding: 8px 12px;
      background: rgba(0,0,0,.3); border-radius: 5px;
      border: 1px solid var(--border); cursor: pointer;
      transition: border-color .15s;
    }
    .history-item:hover { border-color: var(--accent2); }
    .history-item .hi-status { font-weight: 700; }
    .history-item .hi-url { color: var(--muted); flex: 1; truncate: clip; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .history-item .hi-time { color: var(--muted); }

    /* ── Spinner ────────────────────────────── */
    .spinner {
      display: none; width: 16px; height: 16px;
      border: 2px solid rgba(0,255,231,.2);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin .65s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .loading .spinner { display: inline-block; }

    /* ── Scrollbar ──────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

    /* ── Reveal animation ───────────────────── */
    .reveal { opacity: 0; transform: translateY(18px); animation: reveal .5s forwards; }
    .reveal:nth-child(1) { animation-delay: .05s; }
    .reveal:nth-child(2) { animation-delay: .13s; }
    .reveal:nth-child(3) { animation-delay: .21s; }
    .reveal:nth-child(4) { animation-delay: .29s; }
    .reveal:nth-child(5) { animation-delay: .37s; }
    @keyframes reveal { to { opacity:1; transform: translateY(0); } }
  </style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <header class="reveal">
    <div class="badge">Server 1 · Flask · Python</div>
    <h1>Python Flask<br/><span>API Server</span></h1>
    <p class="subtitle">// Dynamic REST client &amp; live response explorer</p>
  </header>

  <!-- Endpoints quick-select -->
  <div class="card reveal">
    <div class="card-title">Available Endpoints</div>
    <div class="endpoints" id="endpointPills">
      <div class="ep-pill active" data-url="/api/ping" data-method="GET">
        <span class="method get">GET</span>/api/ping
      </div>
      <div class="ep-pill" data-url="/api/info" data-method="GET">
        <span class="method get">GET</span>/api/info
      </div>
      <div class="ep-pill" data-url="/api/echo" data-method="POST">
        <span class="method post">POST</span>/api/echo
      </div>
      <div class="ep-pill" data-url="/api/process" data-method="POST">
        <span class="method post">POST</span>/api/process
      </div>
      <div class="ep-pill" data-url="/api/time" data-method="GET">
        <span class="method get">GET</span>/api/time
      </div>
    </div>
  </div>

  <!-- Request Builder -->
  <div class="card reveal">
    <div class="card-title">Request Builder</div>
    <div class="req-row">
      <select id="methodSel" style="width:90px">
        <option>GET</option>
        <option>POST</option>
      </select>
      <input type="text" class="url-input" id="urlInput" value="/api/ping" placeholder="Endpoint path"/>
      <button class="btn btn-primary" id="sendBtn" onclick="sendRequest()">
        <span class="spinner" id="spinner"></span>
        <span id="btnLabel">Send</span>
      </button>
      <button class="btn btn-ghost" onclick="clearResponse()">Clear</button>
    </div>
    <textarea id="bodyInput" placeholder='Request body (JSON) — only for POST&#10;{"key": "value"}'></textarea>
  </div>

  <!-- Response -->
  <div class="card reveal">
    <div class="card-title">Response</div>
    <div class="response-header">
      <span class="status-badge status-idle" id="statusBadge">— Awaiting request</span>
      <span class="response-time" id="respTime"></span>
    </div>
    <pre id="responseBox">// Hit Send to see the response here</pre>
  </div>

  <!-- Server Info -->
  <div class="card reveal">
    <div class="card-title">Server Info</div>
    <div class="info-grid" id="serverInfo">
      <div class="info-item">
        <span class="info-label">Framework</span>
        <span class="info-value">Flask</span>
      </div>
      <div class="info-item">
        <span class="info-label">Python</span>
        <span class="info-value" id="si-python">—</span>
      </div>
      <div class="info-item">
        <span class="info-label">Platform</span>
        <span class="info-value" id="si-platform">—</span>
      </div>
      <div class="info-item">
        <span class="info-label">Uptime</span>
        <span class="info-value" id="si-uptime">—</span>
      </div>
      <div class="info-item">
        <span class="info-label">Host</span>
        <span class="info-value" id="si-host">—</span>
      </div>
      <div class="info-item">
        <span class="info-label">Server Time</span>
        <span class="info-value" id="si-time">—</span>
      </div>
    </div>
  </div>

  <!-- Request History -->
  <div class="card reveal">
    <div class="card-title">Request History</div>
    <div class="history-list" id="historyList">
      <span style="font-family:var(--mono);font-size:12px;color:var(--muted)">No requests yet.</span>
    </div>
  </div>

</div>

<script>
  const history_log = [];
  let startupTime = Date.now();

  // ── Endpoint pills wiring ──────────────────────────────────────
  document.querySelectorAll('.ep-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.ep-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const url    = pill.dataset.url;
      const method = pill.dataset.method;
      document.getElementById('urlInput').value = url;
      document.getElementById('methodSel').value = method;
      if (method === 'POST') {
        document.getElementById('bodyInput').value = '{"message": "hello from client"}';
      } else {
        document.getElementById('bodyInput').value = '';
      }
    });
  });

  // ── Send request ───────────────────────────────────────────────
  async function sendRequest() {
    const btn      = document.getElementById('sendBtn');
    const spinner  = document.getElementById('spinner');
    const label    = document.getElementById('btnLabel');
    const url      = document.getElementById('urlInput').value.trim();
    const method   = document.getElementById('methodSel').value;
    const bodyRaw  = document.getElementById('bodyInput').value.trim();
    const box      = document.getElementById('responseBox');
    const badge    = document.getElementById('statusBadge');
    const timeEl   = document.getElementById('respTime');

    // Loading state
    btn.disabled = true;
    spinner.style.display = 'inline-block';
    label.textContent = 'Sending…';
    box.textContent = '// Waiting for response…';
    badge.className = 'status-badge status-idle';
    badge.textContent = '— Sending';

    const t0 = performance.now();

    try {
      const opts = { method, headers: { 'Content-Type': 'application/json' } };
      if (method === 'POST' && bodyRaw) opts.body = bodyRaw;

      const res  = await fetch(url, opts);
      const ms   = Math.round(performance.now() - t0);
      const json = await res.json();
      const pretty = JSON.stringify(json, null, 2);

      box.textContent = pretty;
      timeEl.textContent = ms + ' ms';

      if (res.ok) {
        badge.className = 'status-badge status-ok';
        badge.textContent = '✓ ' + res.status + ' ' + res.statusText;
      } else {
        badge.className = 'status-badge status-err';
        badge.textContent = '✗ ' + res.status + ' ' + res.statusText;
      }

      addHistory(method, url, res.status, ms);
    } catch (err) {
      const ms = Math.round(performance.now() - t0);
      box.textContent = '// Error: ' + err.message;
      badge.className = 'status-badge status-err';
      badge.textContent = '✗ Network Error';
      timeEl.textContent = ms + ' ms';
      addHistory(method, url, 'ERR', ms);
    } finally {
      btn.disabled = false;
      spinner.style.display = 'none';
      label.textContent = 'Send';
    }
  }

  function clearResponse() {
    document.getElementById('responseBox').textContent = '// Cleared.';
    document.getElementById('statusBadge').className = 'status-badge status-idle';
    document.getElementById('statusBadge').textContent = '— Awaiting request';
    document.getElementById('respTime').textContent = '';
  }

  // ── History ────────────────────────────────────────────────────
  function addHistory(method, url, status, ms) {
    history_log.unshift({ method, url, status, ms, ts: new Date().toLocaleTimeString() });
    renderHistory();
  }

  function renderHistory() {
    const list = document.getElementById('historyList');
    if (!history_log.length) { list.innerHTML = '<span style="font-family:var(--mono);font-size:12px;color:var(--muted)">No requests yet.</span>'; return; }
    list.innerHTML = history_log.slice(0, 20).map((h, i) => `
      <div class="history-item" onclick="replayHistory(${i})">
        <span class="method ${h.method === 'GET' ? 'get' : 'post'}" style="padding:2px 6px;border-radius:3px;font-size:10px;font-weight:700;background:${h.method==='GET'?'rgba(0,255,231,.15)':'rgba(123,97,255,.2)'};color:${h.method==='GET'?'var(--accent)':'var(--accent2)'}">${h.method}</span>
        <span class="hi-url">${h.url}</span>
        <span class="hi-status" style="color:${String(h.status).startsWith('2')?'#00ff64':'var(--danger)'}">${h.status}</span>
        <span class="hi-time">${h.ms}ms</span>
        <span class="hi-time">${h.ts}</span>
      </div>`).join('');
  }

  function replayHistory(i) {
    const h = history_log[i];
    document.getElementById('urlInput').value = h.url;
    document.getElementById('methodSel').value = h.method;
    sendRequest();
  }

  // ── Server info live ───────────────────────────────────────────
  async function fetchServerInfo() {
    try {
      const res  = await fetch('/api/info');
      const data = await res.json();
      document.getElementById('si-python').textContent   = data.python_version  || '—';
      document.getElementById('si-platform').textContent = data.platform         || '—';
      document.getElementById('si-host').textContent     = data.host             || '—';
    } catch (_) {}
  }

  function tickUptime() {
    const s = Math.floor((Date.now() - startupTime) / 1000);
    const h = String(Math.floor(s / 3600)).padStart(2,'0');
    const m = String(Math.floor((s % 3600) / 60)).padStart(2,'0');
    const sec = String(s % 60).padStart(2,'0');
    document.getElementById('si-uptime').textContent = h + ':' + m + ':' + sec;
    document.getElementById('si-time').textContent   = new Date().toLocaleTimeString();
  }

  // Keyboard shortcut: Ctrl/Cmd+Enter → Send
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') sendRequest();
  });

  fetchServerInfo();
  setInterval(tickUptime, 1000);
  tickUptime();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
#  Flask Routes
# ─────────────────────────────────────────────

SERVER_START = datetime.datetime.utcnow()


@app.route("/")
def index():
    """Serve the dynamic single-page UI."""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/ping")
def ping():
    """Health-check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "pong 🏓",
        "server": "Server 1",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    })


@app.route("/api/info")
def info():
    """Return server metadata."""
    uptime_secs = (datetime.datetime.utcnow() - SERVER_START).total_seconds()
    return jsonify({
        "server": "Server 1",
        "framework": "Flask",
        "python_version": sys.version.split()[0],
        "platform": platform.system() + " " + platform.release(),
        "host": os.environ.get("SERVER_HOST", "localhost"),
        "port": int(os.environ.get("PORT", 5000)),
        "uptime_seconds": round(uptime_secs, 2),
        "started_at": SERVER_START.isoformat() + "Z",
        "environment": os.environ.get("FLASK_ENV", "development"),
    })


@app.route("/api/echo", methods=["POST"])
def echo():
    """Echo back the JSON body sent by the client."""
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "status": "ok",
        "echo": payload,
        "received_at": datetime.datetime.utcnow().isoformat() + "Z",
        "content_type": request.content_type,
        "content_length": request.content_length,
    })


@app.route("/api/process", methods=["POST"])
def process():
    """Simple text-processing demo endpoint."""
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "")

    if not message:
        return jsonify({"status": "error", "detail": "Field 'message' is required."}), 400

    result = {
        "status": "ok",
        "original": message,
        "upper": message.upper(),
        "lower": message.lower(),
        "word_count": len(message.split()),
        "char_count": len(message),
        "reversed": message[::-1],
        "processed_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
    return jsonify(result)


@app.route("/api/time")
def current_time():
    """Return current server time in multiple formats."""
    now = datetime.datetime.utcnow()
    return jsonify({
        "utc_iso": now.isoformat() + "Z",
        "utc_date": now.strftime("%Y-%m-%d"),
        "utc_time": now.strftime("%H:%M:%S"),
        "unix_timestamp": int(now.timestamp()),
        "day_of_week": now.strftime("%A"),
    })


# ─────────────────────────────────────────────
#  Error Handlers
# ─────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "detail": "Endpoint not found.", "code": 404}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "error", "detail": "Method not allowed.", "code": 405}), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "detail": "Internal server error.", "code": 500}), 500


# ─────────────────────────────────────────────
#  Entry-point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_ENV", "development") == "development"

    print(f"""
╔══════════════════════════════════════════╗
║          Server 1 · Flask API            ║
╠══════════════════════════════════════════╣
║  → http://{host}:{port}
║  → Python  {sys.version.split()[0]}
║  → Platform {platform.system()}
╚══════════════════════════════════════════╝
""")
    app.run(host=host, port=port, debug=debug)
