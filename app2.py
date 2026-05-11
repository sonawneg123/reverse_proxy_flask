from flask import Flask, request, jsonify, render_template_string
import datetime
import platform
import sys
import os
import hashlib
import random
import string
import json
import math

app = Flask(__name__)

# ─────────────────────────────────────────────
#  Embedded HTML / CSS / JS  — Server 2 UI
# ─────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Server 2 · Flask API</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:       #f5f2ee;
      --surface:  #ffffff;
      --border:   #e2ddd8;
      --ink:      #1a1714;
      --muted:    #8c8680;
      --accent:   #e05a2b;
      --accent2:  #2b6de0;
      --green:    #1a8a4a;
      --mono:     'Space Mono', monospace;
      --sans:     'Outfit', sans-serif;
      --radius:   8px;
      --shadow:   0 2px 12px rgba(26,23,20,.10);
    }

    html { scroll-behavior: smooth; }

    body {
      background: var(--bg);
      color: var(--ink);
      font-family: var(--sans);
      min-height: 100vh;
    }

    /* ── Dot-paper background ─────────────── */
    body::before {
      content: '';
      position: fixed; inset: 0;
      background-image: radial-gradient(circle, #c8c4bf 1px, transparent 1px);
      background-size: 24px 24px;
      opacity: .45;
      pointer-events: none; z-index: 0;
    }

    .wrapper {
      position: relative; z-index: 1;
      max-width: 920px;
      margin: 0 auto;
      padding: 52px 24px 90px;
    }

    /* ── Header ──────────────────────────── */
    header { margin-bottom: 44px; }

    .server-tag {
      display: inline-flex; align-items: center; gap: 7px;
      background: var(--accent); color: #fff;
      font-family: var(--mono); font-size: 11px;
      letter-spacing: .1em; text-transform: uppercase;
      padding: 5px 12px; border-radius: 4px;
      margin-bottom: 20px;
    }
    .server-tag::before {
      content: ''; width: 6px; height: 6px;
      background: rgba(255,255,255,.8); border-radius: 50%;
      animation: pulse 1.6s ease-in-out infinite;
    }
    @keyframes pulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.5);opacity:.5} }

    h1 {
      font-size: clamp(2.2rem, 5vw, 3.4rem);
      font-weight: 800; line-height: 1.05;
      letter-spacing: -.03em; color: var(--ink);
    }
    h1 em { font-style: normal; color: var(--accent); }

    .subtitle {
      margin-top: 10px;
      font-family: var(--mono); font-size: 12px;
      color: var(--muted); letter-spacing: .03em;
    }

    /* ── Cards ───────────────────────────── */
    .card {
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: var(--radius);
      padding: 26px;
      margin-bottom: 20px;
      box-shadow: var(--shadow);
      transition: box-shadow .2s;
    }
    .card:hover { box-shadow: 0 4px 24px rgba(26,23,20,.13); }

    .card-label {
      font-family: var(--mono); font-size: 10px;
      letter-spacing: .15em; text-transform: uppercase;
      color: var(--muted); margin-bottom: 18px;
      display: flex; align-items: center; gap: 8px;
    }
    .card-label::after {
      content: ''; flex: 1; height: 1px; background: var(--border);
    }

    /* ── Endpoints grid ──────────────────── */
    .ep-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
      gap: 10px;
    }

    .ep-card {
      border: 1.5px solid var(--border);
      border-radius: 6px; padding: 12px 14px;
      cursor: pointer; transition: all .16s;
      user-select: none;
    }
    .ep-card:hover { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(224,90,43,.08); }
    .ep-card.active { border-color: var(--accent); background: rgba(224,90,43,.04); }

    .ep-top { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }
    .method-pill {
      font-family: var(--mono); font-size: 9px;
      font-weight: 700; letter-spacing: .08em;
      padding: 2px 7px; border-radius: 3px;
    }
    .get  { background: #e6f4ec; color: var(--green); }
    .post { background: #e8effe; color: var(--accent2); }

    .ep-path {
      font-family: var(--mono); font-size: 12px; color: var(--ink);
    }
    .ep-desc {
      font-size: 11px; color: var(--muted); margin-top: 2px;
    }

    /* ── Request builder ─────────────────── */
    .req-row { display: flex; gap: 10px; align-items: stretch; flex-wrap: wrap; }

    select, input[type="text"], textarea {
      background: var(--bg);
      border: 1.5px solid var(--border);
      border-radius: 6px; color: var(--ink);
      font-family: var(--mono); font-size: 13px;
      padding: 10px 13px;
      transition: border-color .16s, box-shadow .16s;
      outline: none;
    }
    select:focus, input:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(224,90,43,.12);
    }
    input.url-input { flex: 1; min-width: 200px; }
    textarea {
      width: 100%; min-height: 86px;
      resize: vertical; margin-top: 12px;
    }

    /* ── Buttons ─────────────────────────── */
    .btn {
      font-family: var(--mono); font-size: 12px; font-weight: 700;
      letter-spacing: .07em; text-transform: uppercase;
      padding: 10px 22px; border: none; border-radius: 6px;
      cursor: pointer; transition: all .16s; white-space: nowrap;
    }
    .btn-primary {
      background: var(--accent); color: #fff;
    }
    .btn-primary:hover { background: #c44d22; transform: translateY(-1px); box-shadow: 0 4px 14px rgba(224,90,43,.35); }
    .btn-primary:active { transform: translateY(0); }
    .btn-primary:disabled { opacity: .45; cursor: not-allowed; transform: none; box-shadow: none; }

    .btn-ghost {
      background: transparent; color: var(--muted);
      border: 1.5px solid var(--border);
    }
    .btn-ghost:hover { border-color: var(--muted); color: var(--ink); }

    /* ── Response ────────────────────────── */
    .resp-meta {
      display: flex; align-items: center;
      justify-content: space-between; margin-bottom: 12px;
      flex-wrap: wrap; gap: 8px;
    }
    .status-chip {
      font-family: var(--mono); font-size: 11px; font-weight: 700;
      padding: 4px 11px; border-radius: 4px; letter-spacing: .06em;
      transition: all .25s;
    }
    .s-idle { background: #f0ede9; color: var(--muted); }
    .s-ok   { background: #e6f4ec; color: var(--green); }
    .s-err  { background: #fdecea; color: #c0392b; }

    .resp-time { font-family: var(--mono); font-size: 11px; color: var(--muted); }

    pre {
      background: #1a1714; color: #e8e4de;
      border-radius: 7px; padding: 18px;
      font-family: var(--mono); font-size: 12.5px;
      line-height: 1.75; overflow-x: auto;
      min-height: 120px; white-space: pre-wrap;
      word-break: break-word;
    }

    /* syntax coloring */
    .json-key    { color: #7ecde8; }
    .json-str    { color: #a8d8a8; }
    .json-num    { color: #f4b96e; }
    .json-bool   { color: #c792ea; }
    .json-null   { color: #ff6b6b; }

    /* ── Info grid ───────────────────────── */
    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
    }
    .info-cell {
      background: var(--bg);
      border: 1.5px solid var(--border);
      border-radius: 6px; padding: 14px;
    }
    .info-cell .lbl {
      font-family: var(--mono); font-size: 9px;
      letter-spacing: .13em; text-transform: uppercase;
      color: var(--muted); margin-bottom: 6px;
    }
    .info-cell .val {
      font-family: var(--mono); font-size: 13px;
      color: var(--accent); font-weight: 700;
    }

    /* ── History ─────────────────────────── */
    .hist-list { display: flex; flex-direction: column; gap: 7px; max-height: 250px; overflow-y: auto; }
    .hist-item {
      display: flex; align-items: center; gap: 10px;
      font-family: var(--mono); font-size: 11px;
      padding: 8px 12px;
      border: 1.5px solid var(--border);
      border-radius: 5px; cursor: pointer;
      transition: border-color .15s, background .15s;
    }
    .hist-item:hover { border-color: var(--accent2); background: rgba(43,109,224,.04); }
    .hist-url  { flex: 1; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .hist-code { font-weight: 700; }
    .hist-ms   { color: var(--muted); }

    /* ── Compare panel ───────────────────── */
    .compare-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 14px;
    }
    @media(max-width:600px){ .compare-grid { grid-template-columns: 1fr; } }

    .compare-box {
      border: 1.5px solid var(--border); border-radius: 6px;
      overflow: hidden;
    }
    .compare-header {
      background: var(--bg); padding: 8px 14px;
      font-family: var(--mono); font-size: 10px;
      letter-spacing: .1em; text-transform: uppercase;
      color: var(--muted); border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
    }
    .compare-body { padding: 14px; font-family: var(--mono); font-size: 12px; min-height: 80px; }

    /* ── Spinner ─────────────────────────── */
    .spin {
      display: none; width: 14px; height: 14px;
      border: 2px solid rgba(255,255,255,.3);
      border-top-color: #fff; border-radius: 50%;
      animation: rot .6s linear infinite;
    }
    @keyframes rot { to { transform: rotate(360deg); } }

    /* ── Animations ──────────────────────── */
    .fade-up { opacity: 0; transform: translateY(16px); animation: fu .45s forwards; }
    .fade-up:nth-child(1){animation-delay:.04s}
    .fade-up:nth-child(2){animation-delay:.11s}
    .fade-up:nth-child(3){animation-delay:.18s}
    .fade-up:nth-child(4){animation-delay:.25s}
    .fade-up:nth-child(5){animation-delay:.32s}
    .fade-up:nth-child(6){animation-delay:.39s}
    @keyframes fu { to { opacity:1; transform:translateY(0); } }

    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
  </style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <header class="fade-up">
    <div class="server-tag">Server 2 · Flask · Python</div>
    <h1>Flask API<br/><em>Server Two</em></h1>
    <p class="subtitle">// Utilities · Hashing · Text · Math · Data Tools</p>
  </header>

  <!-- Endpoints -->
  <div class="card fade-up">
    <div class="card-label">Endpoints</div>
    <div class="ep-grid" id="epGrid">
      <div class="ep-card active" data-url="/api/status" data-method="GET">
        <div class="ep-top"><span class="method-pill get">GET</span><span class="ep-path">/api/status</span></div>
        <div class="ep-desc">Server health &amp; status</div>
      </div>
      <div class="ep-card" data-url="/api/sysinfo" data-method="GET">
        <div class="ep-top"><span class="method-pill get">GET</span><span class="ep-path">/api/sysinfo</span></div>
        <div class="ep-desc">Full system information</div>
      </div>
      <div class="ep-card" data-url="/api/hash" data-method="POST">
        <div class="ep-top"><span class="method-pill post">POST</span><span class="ep-path">/api/hash</span></div>
        <div class="ep-desc">Hash text (MD5/SHA256/SHA512)</div>
      </div>
      <div class="ep-card" data-url="/api/generate" data-method="POST">
        <div class="ep-top"><span class="method-pill post">POST</span><span class="ep-path">/api/generate</span></div>
        <div class="ep-desc">Random string / token generator</div>
      </div>
      <div class="ep-card" data-url="/api/textstat" data-method="POST">
        <div class="ep-top"><span class="method-pill post">POST</span><span class="ep-path">/api/textstat</span></div>
        <div class="ep-desc">Text statistics &amp; analysis</div>
      </div>
      <div class="ep-card" data-url="/api/math" data-method="POST">
        <div class="ep-top"><span class="method-pill post">POST</span><span class="ep-path">/api/math</span></div>
        <div class="ep-desc">Math expression evaluator</div>
      </div>
      <div class="ep-card" data-url="/api/datetime" data-method="GET">
        <div class="ep-top"><span class="method-pill get">GET</span><span class="ep-path">/api/datetime</span></div>
        <div class="ep-desc">Date &amp; time details</div>
      </div>
      <div class="ep-card" data-url="/api/validate" data-method="POST">
        <div class="ep-top"><span class="method-pill post">POST</span><span class="ep-path">/api/validate</span></div>
        <div class="ep-desc">JSON schema validator</div>
      </div>
    </div>
  </div>

  <!-- Request Builder -->
  <div class="card fade-up">
    <div class="card-label">Request Builder</div>
    <div class="req-row">
      <select id="methodSel" style="width:88px">
        <option>GET</option>
        <option>POST</option>
      </select>
      <input type="text" class="url-input" id="urlInput" value="/api/status" placeholder="Endpoint path"/>
      <button class="btn btn-primary" id="sendBtn" onclick="sendReq()">
        <span class="spin" id="spin"></span>
        <span id="btnLbl">Send ↗</span>
      </button>
      <button class="btn btn-ghost" onclick="clearResp()">Clear</button>
    </div>
    <textarea id="bodyInput" placeholder='JSON body for POST endpoints&#10;&#10;Example for /api/hash:  {"text":"hello","algo":"sha256"}&#10;Example for /api/math:  {"expression":"2**10 + sqrt(144)"}&#10;Example for /api/generate: {"length":32,"type":"hex"}'></textarea>
  </div>

  <!-- Response -->
  <div class="card fade-up">
    <div class="card-label">Response</div>
    <div class="resp-meta">
      <span class="status-chip s-idle" id="statusChip">— idle</span>
      <span class="resp-time" id="respTime"></span>
    </div>
    <pre id="respBox">// Select an endpoint and press Send ↗</pre>
  </div>

  <!-- Compare: Server 1 vs Server 2 -->
  <div class="card fade-up">
    <div class="card-label">Server Comparison</div>
    <div class="compare-grid">
      <div class="compare-box">
        <div class="compare-header">
          <span>Server 1</span>
          <span id="s1-status" style="color:var(--muted)">—</span>
        </div>
        <div class="compare-body" id="s1-info">Loading…</div>
      </div>
      <div class="compare-box">
        <div class="compare-header" style="background:rgba(224,90,43,.06)">
          <span style="color:var(--accent)">Server 2 ← you are here</span>
          <span id="s2-status" style="color:var(--muted)">—</span>
        </div>
        <div class="compare-body" id="s2-info">Loading…</div>
      </div>
    </div>
  </div>

  <!-- System Info Live -->
  <div class="card fade-up">
    <div class="card-label">Live System Info</div>
    <div class="info-grid">
      <div class="info-cell"><div class="lbl">Python</div><div class="val" id="si-py">—</div></div>
      <div class="info-cell"><div class="lbl">Platform</div><div class="val" id="si-plt">—</div></div>
      <div class="info-cell"><div class="lbl">Uptime</div><div class="val" id="si-up">—</div></div>
      <div class="info-cell"><div class="lbl">Server</div><div class="val" id="si-sv">Server 2</div></div>
      <div class="info-cell"><div class="lbl">Port</div><div class="val" id="si-port">—</div></div>
      <div class="info-cell"><div class="lbl">Local Time</div><div class="val" id="si-lt">—</div></div>
    </div>
  </div>

  <!-- History -->
  <div class="card fade-up">
    <div class="card-label">Request History</div>
    <div class="hist-list" id="histList">
      <span style="font-family:var(--mono);font-size:12px;color:var(--muted)">No requests yet.</span>
    </div>
  </div>

</div>

<script>
  const history_log = [];
  const boot = Date.now();

  // ── Endpoint card wiring ─────────────────────────────────────
  const defaultBodies = {
    '/api/hash':     '{"text": "hello world", "algo": "sha256"}',
    '/api/generate': '{"length": 32, "type": "hex"}',
    '/api/textstat': '{"text": "Flask is a lightweight WSGI web application framework in Python."}',
    '/api/math':     '{"expression": "2**10 + sqrt(144)"}',
    '/api/validate': '{"data": {"name": "Alice", "age": 30}, "required_fields": ["name","age"]}',
  };

  document.querySelectorAll('.ep-card').forEach(c => {
    c.addEventListener('click', () => {
      document.querySelectorAll('.ep-card').forEach(x => x.classList.remove('active'));
      c.classList.add('active');
      const url = c.dataset.url, method = c.dataset.method;
      document.getElementById('urlInput').value = url;
      document.getElementById('methodSel').value = method;
      document.getElementById('bodyInput').value = defaultBodies[url] || '';
    });
  });

  // ── JSON syntax highlighter ──────────────────────────────────
  function highlight(json) {
    return json
      .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, match => {
        if (/^"/.test(match)) {
          return /:$/.test(match)
            ? `<span class="json-key">${match}</span>`
            : `<span class="json-str">${match}</span>`;
        }
        if (/true|false/.test(match)) return `<span class="json-bool">${match}</span>`;
        if (/null/.test(match))        return `<span class="json-null">${match}</span>`;
        return `<span class="json-num">${match}</span>`;
      });
  }

  // ── Send ─────────────────────────────────────────────────────
  async function sendReq() {
    const btn    = document.getElementById('sendBtn');
    const spin   = document.getElementById('spin');
    const lbl    = document.getElementById('btnLbl');
    const url    = document.getElementById('urlInput').value.trim();
    const method = document.getElementById('methodSel').value;
    const body   = document.getElementById('bodyInput').value.trim();
    const box    = document.getElementById('respBox');
    const chip   = document.getElementById('statusChip');
    const timeEl = document.getElementById('respTime');

    btn.disabled = true;
    spin.style.display = 'inline-block';
    lbl.textContent = 'Sending…';
    box.innerHTML = '// Waiting…';
    chip.className = 'status-chip s-idle';
    chip.textContent = '— sending';

    const t0 = performance.now();
    try {
      const opts = { method, headers: { 'Content-Type': 'application/json' } };
      if (method === 'POST' && body) opts.body = body;

      const res  = await fetch(url, opts);
      const ms   = Math.round(performance.now() - t0);
      const data = await res.json();
      const pretty = JSON.stringify(data, null, 2);

      box.innerHTML = highlight(pretty);
      timeEl.textContent = ms + ' ms';

      if (res.ok) {
        chip.className = 'status-chip s-ok';
        chip.textContent = '✓ ' + res.status + ' OK';
      } else {
        chip.className = 'status-chip s-err';
        chip.textContent = '✗ ' + res.status;
      }
      pushHistory(method, url, res.status, ms);
    } catch(e) {
      const ms = Math.round(performance.now() - t0);
      box.innerHTML = '// Error: ' + e.message;
      chip.className = 'status-chip s-err';
      chip.textContent = '✗ Network Error';
      timeEl.textContent = ms + ' ms';
      pushHistory(method, url, 'ERR', ms);
    } finally {
      btn.disabled = false;
      spin.style.display = 'none';
      lbl.textContent = 'Send ↗';
    }
  }

  function clearResp() {
    document.getElementById('respBox').innerHTML = '// Cleared.';
    const chip = document.getElementById('statusChip');
    chip.className = 'status-chip s-idle';
    chip.textContent = '— idle';
    document.getElementById('respTime').textContent = '';
  }

  // ── History ───────────────────────────────────────────────────
  function pushHistory(method, url, code, ms) {
    history_log.unshift({ method, url, code, ms, ts: new Date().toLocaleTimeString() });
    renderHistory();
  }
  function renderHistory() {
    const el = document.getElementById('histList');
    if (!history_log.length) { el.innerHTML = '<span style="font-family:var(--mono);font-size:12px;color:var(--muted)">No requests yet.</span>'; return; }
    el.innerHTML = history_log.slice(0,20).map((h,i) => {
      const ok = String(h.code).startsWith('2');
      const mc = h.method === 'GET' ? 'get' : 'post';
      return `<div class="hist-item" onclick="replayHist(${i})">
        <span class="method-pill ${mc}">${h.method}</span>
        <span class="hist-url">${h.url}</span>
        <span class="hist-code" style="color:${ok?'var(--green)':'#c0392b'}">${h.code}</span>
        <span class="hist-ms">${h.ms}ms</span>
        <span class="hist-ms">${h.ts}</span>
      </div>`;
    }).join('');
  }
  function replayHist(i) {
    const h = history_log[i];
    document.getElementById('urlInput').value  = h.url;
    document.getElementById('methodSel').value = h.method;
    sendReq();
  }

  // ── Live system info ──────────────────────────────────────────
  async function fetchSysInfo() {
    try {
      const r = await fetch('/api/sysinfo');
      const d = await r.json();
      document.getElementById('si-py').textContent   = d.python_version || '—';
      document.getElementById('si-plt').textContent  = d.platform       || '—';
      document.getElementById('si-port').textContent = d.port           || '—';
    } catch(_){}
  }

  function tickClock() {
    const s = Math.floor((Date.now() - boot) / 1000);
    const h = String(Math.floor(s/3600)).padStart(2,'0');
    const m = String(Math.floor((s%3600)/60)).padStart(2,'0');
    const sec = String(s%60).padStart(2,'0');
    document.getElementById('si-up').textContent = `${h}:${m}:${sec}`;
    document.getElementById('si-lt').textContent = new Date().toLocaleTimeString();
  }

  // ── Server comparison panel ───────────────────────────────────
  async function loadComparison() {
    // Server 2 (self)
    try {
      const r = await fetch('/api/sysinfo');
      const d = await r.json();
      document.getElementById('s2-status').textContent = '● online';
      document.getElementById('s2-status').style.color = 'var(--green)';
      document.getElementById('s2-info').innerHTML = `
        <div style="font-family:var(--mono);font-size:11px;line-height:2;color:var(--ink)">
          <b>Python:</b> ${d.python_version}<br/>
          <b>Port:</b>   ${d.port}<br/>
          <b>Endpoints:</b> 8<br/>
          <b>Focus:</b> Utils · Hash · Math
        </div>`;
    } catch(_) {
      document.getElementById('s2-status').textContent = '✗ error';
      document.getElementById('s2-status').style.color = '#c0392b';
    }

    // Server 1 (try to reach on port 5000)
    try {
      const r = await fetch('http://localhost:5000/api/info', { signal: AbortSignal.timeout(2000) });
      const d = await r.json();
      document.getElementById('s1-status').textContent = '● online';
      document.getElementById('s1-status').style.color = 'var(--green)';
      document.getElementById('s1-info').innerHTML = `
        <div style="font-family:var(--mono);font-size:11px;line-height:2;color:var(--ink)">
          <b>Python:</b> ${d.python_version}<br/>
          <b>Port:</b>   ${d.port}<br/>
          <b>Endpoints:</b> 5<br/>
          <b>Focus:</b> Core · Echo · Ping
        </div>`;
    } catch(_) {
      document.getElementById('s1-status').textContent = '○ offline / unreachable';
      document.getElementById('s1-info').innerHTML = `<span style="font-family:var(--mono);font-size:11px;color:var(--muted)">Start Server 1 on port 5000 to see its details here.</span>`;
    }
  }

  // Keyboard shortcut
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey||e.metaKey) && e.key==='Enter') sendReq();
  });

  fetchSysInfo();
  loadComparison();
  setInterval(tickClock, 1000);
  tickClock();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
#  Flask Routes — Server 2
# ─────────────────────────────────────────────

SERVER_START = datetime.datetime.utcnow()
SERVER_NAME  = "Server 2"


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


# ── Health ────────────────────────────────────
@app.route("/api/status")
def status():
    uptime = (datetime.datetime.utcnow() - SERVER_START).total_seconds()
    return jsonify({
        "server":         SERVER_NAME,
        "status":         "ok",
        "uptime_seconds": round(uptime, 2),
        "timestamp":      datetime.datetime.utcnow().isoformat() + "Z",
        "framework":      "Flask",
        "version":        "2",
    })


# ── Full System Info ──────────────────────────
@app.route("/api/sysinfo")
def sysinfo():
    uptime = (datetime.datetime.utcnow() - SERVER_START).total_seconds()
    return jsonify({
        "server":          SERVER_NAME,
        "python_version":  sys.version.split()[0],
        "platform":        platform.system() + " " + platform.release(),
        "machine":         platform.machine(),
        "processor":       platform.processor() or "unknown",
        "python_impl":     platform.python_implementation(),
        "host":            os.environ.get("SERVER_HOST", "localhost"),
        "port":            int(os.environ.get("PORT", 5001)),
        "environment":     os.environ.get("FLASK_ENV", "development"),
        "started_at":      SERVER_START.isoformat() + "Z",
        "uptime_seconds":  round(uptime, 2),
        "pid":             os.getpid(),
    })


# ── Hashing ───────────────────────────────────
@app.route("/api/hash", methods=["POST"])
def hash_text():
    payload = request.get_json(silent=True) or {}
    text    = payload.get("text", "")
    algo    = payload.get("algo", "sha256").lower()

    if not text:
        return jsonify({"status": "error", "detail": "Field 'text' is required."}), 400

    supported = {"md5": hashlib.md5, "sha256": hashlib.sha256, "sha512": hashlib.sha512, "sha1": hashlib.sha1}
    if algo not in supported:
        return jsonify({"status": "error", "detail": f"Unsupported algo. Choose from: {list(supported.keys())}"}), 400

    encoded = text.encode("utf-8")
    digest  = supported[algo](encoded).hexdigest()

    return jsonify({
        "status":      "ok",
        "algorithm":   algo,
        "input":       text,
        "input_bytes": len(encoded),
        "hash":        digest,
        "hash_length": len(digest),
        "timestamp":   datetime.datetime.utcnow().isoformat() + "Z",
    })


# ── Random Generator ──────────────────────────
@app.route("/api/generate", methods=["POST"])
def generate():
    payload = request.get_json(silent=True) or {}
    length  = min(int(payload.get("length", 32)), 512)
    kind    = payload.get("type", "hex").lower()

    if kind == "hex":
        result = ''.join(random.choices("0123456789abcdef", k=length))
    elif kind == "alpha":
        result = ''.join(random.choices(string.ascii_letters, k=length))
    elif kind == "alphanumeric":
        result = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    elif kind == "numeric":
        result = ''.join(random.choices(string.digits, k=length))
    elif kind == "uuid":
        import uuid
        result = str(uuid.uuid4())
        length = len(result)
    else:
        return jsonify({"status": "error", "detail": "type must be: hex | alpha | alphanumeric | numeric | uuid"}), 400

    return jsonify({
        "status":    "ok",
        "type":      kind,
        "length":    length,
        "result":    result,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    })


# ── Text Statistics ───────────────────────────
@app.route("/api/textstat", methods=["POST"])
def textstat():
    payload = request.get_json(silent=True) or {}
    text    = payload.get("text", "")

    if not text:
        return jsonify({"status": "error", "detail": "Field 'text' is required."}), 400

    words     = text.split()
    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    lines     = text.splitlines()
    unique_w  = set(w.lower().strip(".,!?\"'") for w in words)

    return jsonify({
        "status":          "ok",
        "characters":      len(text),
        "characters_no_space": len(text.replace(" ", "")),
        "words":           len(words),
        "unique_words":    len(unique_w),
        "sentences":       len(sentences),
        "lines":           len(lines),
        "paragraphs":      len([l for l in lines if l.strip()]),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 2),
        "avg_words_per_sentence": round(len(words) / max(len(sentences), 1), 2),
        "most_common_words": sorted(
            [(w, words.count(w)) for w in unique_w],
            key=lambda x: -x[1]
        )[:5],
        "is_palindrome":   text.replace(" ", "").lower() == text.replace(" ", "").lower()[::-1],
        "timestamp":       datetime.datetime.utcnow().isoformat() + "Z",
    })


# ── Math Evaluator ────────────────────────────
SAFE_MATH = {
    "sqrt": math.sqrt, "pow": math.pow, "abs": abs,
    "ceil": math.ceil, "floor": math.floor, "round": round,
    "log": math.log, "log10": math.log10, "log2": math.log2,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "pi": math.pi, "e": math.e, "inf": math.inf,
    "factorial": math.factorial, "gcd": math.gcd,
}

@app.route("/api/math", methods=["POST"])
def math_eval():
    payload    = request.get_json(silent=True) or {}
    expression = payload.get("expression", "").strip()

    if not expression:
        return jsonify({"status": "error", "detail": "Field 'expression' is required."}), 400
    if len(expression) > 200:
        return jsonify({"status": "error", "detail": "Expression too long (max 200 chars)."}), 400

    try:
        result = eval(expression, {"__builtins__": {}}, SAFE_MATH)  # restricted eval
        return jsonify({
            "status":     "ok",
            "expression": expression,
            "result":     result,
            "result_str": str(result),
            "is_integer": isinstance(result, (int, float)) and float(result).is_integer(),
            "timestamp":  datetime.datetime.utcnow().isoformat() + "Z",
        })
    except ZeroDivisionError:
        return jsonify({"status": "error", "detail": "Division by zero."}), 400
    except Exception as ex:
        return jsonify({"status": "error", "detail": f"Evaluation error: {str(ex)}"}), 400


# ── DateTime Details ──────────────────────────
@app.route("/api/datetime")
def dt_details():
    now   = datetime.datetime.utcnow()
    local = datetime.datetime.now()
    return jsonify({
        "utc_iso":          now.isoformat() + "Z",
        "local_iso":        local.isoformat(),
        "utc_date":         now.strftime("%Y-%m-%d"),
        "utc_time":         now.strftime("%H:%M:%S"),
        "day_of_week":      now.strftime("%A"),
        "day_of_year":      now.timetuple().tm_yday,
        "week_of_year":     now.isocalendar()[1],
        "unix_timestamp":   int(now.timestamp()),
        "quarter":          (now.month - 1) // 3 + 1,
        "is_leap_year":     now.year % 4 == 0 and (now.year % 100 != 0 or now.year % 400 == 0),
        "days_in_month":    [31,28+int(now.year%4==0),31,30,31,30,31,31,30,31,30,31][now.month-1],
    })


# ── JSON Validator ────────────────────────────
@app.route("/api/validate", methods=["POST"])
def validate_json():
    payload        = request.get_json(silent=True) or {}
    data           = payload.get("data")
    required_fields = payload.get("required_fields", [])

    if data is None:
        return jsonify({"status": "error", "detail": "Field 'data' is required."}), 400

    missing   = [f for f in required_fields if f not in (data if isinstance(data, dict) else {})]
    is_valid  = len(missing) == 0

    return jsonify({
        "status":          "ok",
        "valid":           is_valid,
        "data_type":       type(data).__name__,
        "required_fields": required_fields,
        "missing_fields":  missing,
        "field_count":     len(data) if isinstance(data, dict) else None,
        "fields_present":  list(data.keys()) if isinstance(data, dict) else None,
        "timestamp":       datetime.datetime.utcnow().isoformat() + "Z",
    })


# ── Error Handlers ────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "server": SERVER_NAME, "detail": "Endpoint not found.", "code": 404}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "error", "server": SERVER_NAME, "detail": "Method not allowed.", "code": 405}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "server": SERVER_NAME, "detail": "Internal server error.", "code": 500}), 500


# ─────────────────────────────────────────────
#  Entry-point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5001))
    host  = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_ENV", "development") == "development"

    print(f"""
╔══════════════════════════════════════════╗
║          Server 2 · Flask API            ║
╠══════════════════════════════════════════╣
║  → http://{host}:{port}
║  → Python  {sys.version.split()[0]}
║  → Platform {platform.system()}
╠══════════════════════════════════════════╣
║  Endpoints:                              ║
║    GET  /api/status                      ║
║    GET  /api/sysinfo                     ║
║    POST /api/hash                        ║
║    POST /api/generate                    ║
║    POST /api/textstat                    ║
║    POST /api/math                        ║
║    GET  /api/datetime                    ║
║    POST /api/validate                    ║
╚══════════════════════════════════════════╝
""")
    app.run(host=host, port=port, debug=debug)
