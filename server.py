import os
import json
import base64
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import httpx
import uvicorn

app = FastAPI(title="Jarvis Prime Voice Matrix")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

async def call_gemini(prompt: str, base64_data: str = None, mime_type: str = "image/jpeg"):
    if not GEMINI_KEY: return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    parts = [{"text": prompt or "इस मीडिया का विश्लेषण करें।"}]
    if base64_data:
        parts.append({"inline_data": {"mime_type": mime_type, "data": base64_data}})
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, json={"contents": [{"parts": parts}]})
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception: pass
    return None

async def call_groq(prompt: str):
    if not GROQ_KEY: return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are Jarvis Prime. Talk naturally, concisely and conversationally for voice interaction."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
    except Exception: pass
    return None

async def call_deepseek(prompt: str):
    if not DEEPSEEK_KEY: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are Jarvis Logic Core. Provide sharp analytical and coding answers."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
    except Exception: pass
    return None

async def call_openai(prompt: str):
    if not OPENAI_KEY: return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are Jarvis Prime. Provide polite, clear and helpful answers."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
    except Exception: pass
    return None

async def route_task(prompt: str, media: str = None, mime: str = "image/jpeg", mode: str = "turbo"):
    if media:
        ans = await call_gemini(prompt, media, mime)
        if ans: return ans, "विजन कोर (Gemini)"

    if mode == "logic" or any(k in prompt.lower() for k in ["code", "python", "गणित", "script", "प्रोग्राम", "logic"]):
        ans = await call_deepseek(prompt)
        if ans: return ans, "लॉजिक कोर (DeepSeek)"
        ans = await call_openai(prompt)
        if ans: return ans, "कन्वर्सेशन कोर (OpenAI)"

    ans = await call_groq(prompt)
    if ans: return ans, "टर्बो कोर (Groq)"

    ans = await call_openai(prompt)
    if ans: return ans, "कन्वर्सेशन कोर (OpenAI)"

    ans = await call_gemini(prompt)
    if ans: return ans, "विजन कोर (Gemini)"

    return "सिस्टम पुनः तैयार हो रहा है।", "सिस्टम सुरक्षा"

@app.post("/chat")
async def chat_endpoint(req: Request):
    try:
        body = await req.json()
        prompt = body.get("message", "")
        media = body.get("image", None)
        mime = body.get("mime_type", "image/jpeg")
        mode = body.get("mode", "turbo")

        reply, core = await route_task(prompt, media, mime, mode)
        return JSONResponse({"reply": reply, "core": core, "response": reply})
    except Exception as e:
        return JSONResponse({"reply": f"त्रुटि: {str(e)}", "core": "Error"}, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def serve_app():
    return """<!DOCTYPE html>
<html lang="hi" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>JARVIS PRIME</title>
  <style>
    :root {
      --bg: #070d18;
      --card-bg: #0c1427;
      --bubble-ai: #111c33;
      --bubble-ai-border: #1e293b;
      --text-main: #f8fafc;
      --text-sub: #94a3b8;
      --accent: #00f0ff;
      --input-bg: #111c33;
      --border: #1e293b;
      --user-bubble: #2563eb;
    }

    [data-theme="light"] {
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --bubble-ai: #f1f5f9;
      --bubble-ai-border: #e2e8f0;
      --text-main: #0f172a;
      --text-sub: #64748b;
      --accent: #0284c7;
      --input-bg: #ffffff;
      --border: #e2e8f0;
      --user-bubble: #0284c7;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; transition: background 0.2s, color 0.2s; }
    body { background-color: var(--bg); color: var(--text-main); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

    /* हेडर */
    .header { padding: 12px 16px; background: var(--card-bg); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; z-index: 50; }
    .header-left { display: flex; align-items: center; gap: 10px; }
    .jarvis-core-pulse { width: 14px; height: 14px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px var(--accent); animation: pulse 2s infinite ease-in-out; }
    @keyframes pulse { 0%, 100% { transform: scale(0.9); opacity: 0.8; } 50% { transform: scale(1.15); opacity: 1; } }
    .header-text h1 { font-size: 15px; letter-spacing: 1px; color: var(--accent); font-weight: 700; }
    .header-text p { font-size: 10px; color: var(--text-sub); }
    
    .header-right { display: flex; align-items: center; gap: 8px; }
    .voice-launch-btn { background: var(--bubble-ai); border: 1px solid var(--accent); color: var(--accent); border-radius: 20px; padding: 4px 10px; font-size: 11px; font-weight: bold; display: flex; align-items: center; gap: 4px; cursor: pointer; }
    .dots-btn { background: none; border: none; color: var(--text-sub); font-size: 22px; cursor: pointer; padding: 0 4px; }

    /* थ्री डॉट्स सेटिंग्स मेन्यू */
    .settings-dropdown { position: absolute; top: 55px; right: 14px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; width: 230px; display: none; flex-direction: column; padding: 8px 0; z-index: 200; box-shadow: 0 8px 25px rgba(0,0,0,0.4); }
    .menu-row { padding: 10px 16px; font-size: 13px; color: var(--text-main); cursor: pointer; display: flex; align-items: center; justify-content: space-between; }
    .menu-row:hover { background: var(--bubble-ai); color: var(--accent); }
    .menu-divider { height: 1px; background: var(--border); margin: 4px 0; }

    /* ड्रॉअर / स्लाइडर्स */
    .drawer { position: fixed; top: 0; right: -300px; width: 300px; height: 100vh; background: var(--card-bg); border-left: 1px solid var(--border); z-index: 300; transition: right 0.3s ease; display: flex; flex-direction: column; }
    .drawer-header { padding: 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
    .drawer-header h2 { font-size: 15px; color: var(--accent); }
    .close-btn { background: none; border: none; color: var(--text-sub); font-size: 20px; cursor: pointer; }
    .drawer-content { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }

    /* चैट एरिया */
    .chat-box { flex: 1; padding: 14px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
    .message { max-width: 86%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.4; word-break: break-word; }
    .user { align-self: flex-end; background: var(--user-bubble); color: #fff; border-bottom-right-radius: 2px; }
    .jarvis { align-self: flex-start; background: var(--bubble-ai); color: var(--text-main); border-bottom-left-radius: 2px; border: 1px solid var(--bubble-ai-border); }
    .core-tag { font-size: 9px; text-transform: uppercase; margin-bottom: 4px; color: var(--accent); font-weight: bold; }
    .preview-media { max-width: 100%; max-height: 180px; border-radius: 8px; margin-bottom: 6px; display: block; }

    /* इनपुट बार */
    .input-bar { padding: 10px 12px; background: var(--card-bg); border-top: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }
    .action-icon-btn { width: 38px; height: 38px; border-radius: 50%; background: var(--input-bg); border: 1px solid var(--border); color: var(--accent); font-size: 18px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
    .input-field { flex: 1; background: var(--input-bg); border: 1px solid var(--border); color: var(--text-main); padding: 9px 14px; border-radius: 20px; font-size: 14px; outline: none; }
    .send-btn { width: 38px; height: 38px; border-radius: 50%; background: var(--accent); border: none; color: #000; font-size: 16px; font-weight: bold; display: flex; align-items: center; justify-content: center; cursor: pointer; }

    /* फुल स्क्रीन वॉइस मोड ORB */
    .voice-modal { position: fixed; inset: 0; background: rgba(7, 13, 24, 0.96); backdrop-filter: blur(15px); z-index: 500; display: none; flex-direction: column; align-items: center; justify-content: space-between; padding: 40px 20px; }
    .orb-container { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 25px; }
    .voice-orb { width: 140px; height: 140px; border-radius: 50%; background: radial-gradient(circle, #00f0ff 0%, #0044ff 70%); box-shadow: 0 0 45px rgba(0, 240, 255, 0.5); transition: transform 0.2s; }
    .voice-orb.listening { animation: orbListen 1.5s infinite alternate; }
    .voice-orb.speaking { animation: orbSpeak 0.8s infinite alternate; box-shadow: 0 0 60px rgba(0, 240, 255, 0.9); }
    @keyframes orbListen { from { transform: scale(0.95); opacity: 0.7; } to { transform: scale(1.1); opacity: 1; } }
    @keyframes orbSpeak { from { transform: scale(1); filter: hue-rotate(0deg); } to { transform: scale(1.25); filter: hue-rotate(60deg); } }
    .voice-status-text { font-size: 16px; color: #38bdf8; font-weight: 500; text-align: center; }
    .voice-transcript { font-size: 13px; color: #94a3b8; max-width: 320px; text-align: center; min-height: 40px; }
    .close-voice-btn { background: #ef4444; color: #fff; border: none; border-radius: 50%; width: 55px; height: 55px; font-size: 20px; cursor: pointer; }

    /* मीडिया अटैच मेन्यू */
    .menu-overlay { position: fixed; bottom: 65px; left: 12px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; display: none; flex-direction: column; padding: 6px; gap: 4px; z-index: 100; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
    .media-btn { background: transparent; border: none; color: var(--text-main); padding: 10px 14px; font-size: 13px; text-align: left; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px; }
    .media-btn:hover { background: var(--bubble-ai); color: var(--accent); }
    .staged-container { padding: 6px 14px; background: var(--card-bg); display: none; align-items: center; gap: 10px; border-top: 1px solid var(--border); }
    .staged-thumb { width: 38px; height: 38px; object-fit: cover; border-radius: 6px; border: 1px solid var(--accent); }
    input[type="file"] { display: none; }
  </style>
</head>
<body>

  <!-- हेडर -->
  <div class="header">
    <div class="header-left">
      <div class="jarvis-core-pulse"></div>
      <div class="header-text">
        <h1>JARVIS PRIME</h1>
        <p id="modeBadge">टर्बो (1s) • ऑनलाइन</p>
      </div>
    </div>
    <div class="header-right">
      <button class="voice-launch-btn" onclick="openVoiceMode()">🎙️ लाइव वॉइस</button>
      <button class="dots-btn" onclick="toggleSettings()">⋮</button>
    </div>
  </div>

  <!-- थ्री-डॉट्स मेन्यू -->
  <div class="settings-dropdown" id="settingsDropdown">
    <div class="menu-row" onclick="openDrawer('historyDrawer')">🕒 सर्च हिस्ट्री <span>›</span></div>
    <div class="menu-row" onclick="openDrawer('notesDrawer')">📝 इंस्टेंट नोट्स <span>›</span></div>
    <div class="menu-row" onclick="toggleFlashlight()">🔦 फ़्लैशलाइट (टॉर्च) <span id="torchStatus">बंद</span></div>
    <div class="menu-divider"></div>
    <div class="menu-row" onclick="toggleTheme()">🌓 थीम बदलें <span id="themeLabel">लाइट</span></div>
    <div class="menu-divider"></div>
    <div style="padding: 4px 16px; font-size: 10px; color: var(--text-sub); text-transform: uppercase;">प्रोसेसर स्पीड</div>
    <div class="menu-row" onclick="setSpeed('turbo')">⚡ सुपर टर्बो (1s)</div>
    <div class="menu-row" onclick="setSpeed('logic')">🧠 डीप लॉजिक (DeepSeek)</div>
    <div class="menu-row" onclick="setSpeed('slow')">🐢 शांत / स्लो मोड</div>
    <div class="menu-divider"></div>
    <div class="menu-row" onclick="openDrawer('voiceSettingsDrawer')">🗣️ आवाज़ सेटिंग <span>›</span></div>
  </div>

  <!-- हिस्ट्री ड्रॉअर -->
  <div class="drawer" id="historyDrawer">
    <div class="drawer-header">
      <h2>सर्च हिस्ट्री</h2>
      <button class="close-btn" onclick="closeDrawer('historyDrawer')">✕</button>
    </div>
    <div class="drawer-content" id="historyList"></div>
    <button style="margin:12px; padding:10px; background:#ef4444; color:#fff; border:none; border-radius:8px;" onclick="clearHistory()">हिस्ट्री साफ़ करें</button>
  </div>

  <!-- नोट्स ड्रॉअर -->
  <div class="drawer" id="notesDrawer">
    <div class="drawer-header">
      <h2>त्वरित नोट्स</h2>
      <button class="close-btn" onclick="closeDrawer('notesDrawer')">✕</button>
    </div>
    <div class="drawer-content">
      <textarea id="notesArea" style="width:100%; height:200px; background:var(--input-bg); color:var(--text-main); border:1px solid var(--border); border-radius:8px; padding:10px; font-size:13px;" placeholder="यहाँ अपने नोट्स लिखें..."></textarea>
      <button style="padding:10px; background:var(--accent); color:#000; border:none; border-radius:8px; font-weight:bold;" onclick="saveNotes()">नोट्स सेव करें</button>
    </div>
  </div>

  <!-- आवाज़ सेटिंग्स ड्रॉअर -->
  <div class="drawer" id="voiceSettingsDrawer">
    <div class="drawer-header">
      <h2>आवाज़ सेटिंग्स</h2>
      <button class="close-btn" onclick="closeDrawer('voiceSettingsDrawer')">✕</button>
    </div>
    <div class="drawer-content">
      <label style="font-size:12px; color:var(--text-sub);">आवाज़ चुनें (Voice Type):</label>
      <select id="voiceSelect" style="padding:8px; background:var(--input-bg); color:var(--text-main); border:1px solid var(--border); border-radius:6px;"></select>
      
      <label style="font-size:12px; color:var(--text-sub); margin-top:10px;">बोलने की गति (Speech Pitch/Rate):</label>
      <input type="range" id="voiceRate" min="0.7" max="1.4" step="0.1" value="1.0">
    </div>
  </div>

  <!-- चैट एरिया -->
  <div class="chat-box" id="chatBox">
    <div class="message jarvis">
      <div class="core-tag">JARVIS V5</div>
      नमस्ते! मैं सक्रिय हूँ। आप बोलकर (🎙️), लिखकर या कैमरा/वीडियो से कुछ भी पूछ सकते हैं।
    </div>
  </div>

  <!-- मीडिया प्रीव्यू बार -->
  <div class="staged-container" id="stagedContainer">
    <img id="stagedThumb" class="staged-thumb" src="" alt="Thumbnail">
    <span id="stagedText" style="font-size: 12px; color: var(--text-sub); flex:1;">मीडिया तैयार है</span>
    <button style="background:#ef4444; color:#fff; border:none; border-radius:50%; width:20px; height:20px;" onclick="clearMedia()">✕</button>
  </div>

  <!-- प्लस मेन्यू -->
  <div class="menu-overlay" id="menuOverlay">
    <button class="media-btn" onclick="triggerFile('cameraInput')">📷 लाइव कैमरा</button>
    <button class="media-btn" onclick="triggerFile('galleryInput')">🖼️ गैलरी फ़ोटो</button>
    <button class="media-btn" onclick="triggerFile('videoInput')">🎥 वीडियो फ़ाइल</button>
  </div>

  <input type="file" id="cameraInput" accept="image/*" capture="environment">
  <input type="file" id="galleryInput" accept="image/*">
  <input type="file" id="videoInput" accept="video/*">

  <!-- इनपुट बार -->
  <div class="input-bar">
    <button class="action-icon-btn" onclick="toggleMenu()">+</button>
    <input type="text" id="userInput" class="input-field" placeholder="Jarvis से पूछें..." onkeydown="if(event.key==='Enter') sendChat()">
    <button class="send-btn" onclick="sendChat()">⚡</button>
  </div>

  <!-- फुल स्क्रीन रियल-टाइम वॉइस मोड (ChatGPT जैसा Orb) -->
  <div class="voice-modal" id="voiceModal">
    <div style="font-size:14px; color:#38bdf8; letter-spacing:1px; font-weight:bold;">JARVIS LIVE VOICE MODE</div>
    <div class="orb-container">
      <div class="voice-orb" id="voiceOrb"></div>
      <div class="voice-status-text" id="voiceStatus">सुन रहा हूँ... बोलिए</div>
      <div class="voice-transcript" id="voiceTranscript">आप जो बोलेंगे यहाँ दिखेगा...</div>
    </div>
    <button class="close-voice-btn" onclick="closeVoiceMode()">✕</button>
  </div>

  <script>
    let currentMode = "turbo";
    let currentBase64 = null;
    let currentMimeType = null;
    let torchTrack = null;
    let recognition = null;
    let synth = window.speechSynthesis;
    let isVoiceModalOpen = false;

    // थीम टॉगल (डार्क / लाइट)
    function toggleTheme() {
      const html = document.documentElement;
      const isDark = html.getAttribute('data-theme') === 'dark';
      html.setAttribute('data-theme', isDark ? 'light' : 'dark');
      document.getElementById('themeLabel').innerText = isDark ? 'डार्क' : 'लाइट';
      toggleSettings();
    }

    // मेन्यू और ड्रॉअर
    function toggleSettings() {
      const d = document.getElementById('settingsDropdown');
      d.style.display = d.style.display === 'flex' ? 'none' : 'flex';
    }

    function openDrawer(id) {
      toggleSettings();
      document.getElementById(id).style.right = '0px';
      if(id === 'historyDrawer') loadHistory();
      if(id === 'notesDrawer') document.getElementById('notesArea').value = localStorage.getItem('jarvis_notes') || '';
    }

    function closeDrawer(id) {
      document.getElementById(id).style.right = '-300px';
    }

    function setSpeed(mode) {
      currentMode = mode;
      document.getElementById('modeBadge').innerText = mode === 'turbo' ? 'सुपर टर्बो (1s)' : (mode === 'logic' ? 'डीप लॉजिक' : 'स्लो मोड');
      toggleSettings();
    }

    // सर्च हिस्ट्री
    function saveHistory(q) {
      let h = JSON.parse(localStorage.getItem('j_hist') || '[]');
      h.unshift({ q, t: new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) });
      if(h.length > 40) h.pop();
      localStorage.setItem('j_hist', JSON.stringify(h));
    }

    function loadHistory() {
      const el = document.getElementById('historyList');
      el.innerHTML = '';
      let h = JSON.parse(localStorage.getItem('j_hist') || '[]');
      if(!h.length) { el.innerHTML = '<div style="color:var(--text-sub); text-align:center;">कोई सर्च नहीं।</div>'; return; }
      h.forEach(item => {
        const d = document.createElement('div');
        d.style = "background:var(--input-bg); padding:10px; border-radius:8px; border:1px solid var(--border); cursor:pointer;";
        d.innerHTML = `<div>${item.q}</div><div style="font-size:10px; color:var(--text-sub);">${item.t}</div>`;
        d.onclick = () => { document.getElementById('userInput').value = item.q; closeDrawer('historyDrawer'); };
        el.appendChild(d);
      });
    }

    function clearHistory() {
      localStorage.removeItem('j_hist');
      loadHistory();
    }

    function saveNotes() {
      localStorage.setItem('jarvis_notes', document.getElementById('notesArea').value);
      alert('नोट्स सुरक्षित कर लिए गए हैं!');
    }

    // फ़्लैशलाइट टॉर्च
    async function toggleFlashlight() {
      try {
        if (!torchTrack) {
          const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
          torchTrack = stream.getVideoTracks()[0];
          await torchTrack.applyConstraints({ advanced: [{ torch: true }] });
          document.getElementById('torchStatus').innerText = "चालू";
        } else {
          torchTrack.stop();
          torchTrack = null;
          document.getElementById('torchStatus').innerText = "बंद";
        }
      } catch (e) {
        alert("फ़्लैशलाइट सपोर्ट केवल सपोर्टेड मोबाइल डिवाइसेज पर उपलब्ध है।");
      }
      toggleSettings();
    }

    // आवाज़ सेलेक्टर लोड करना
    function loadVoices() {
      const select = document.getElementById('voiceSelect');
      select.innerHTML = '';
      synth.getVoices().forEach((v, i) => {
        const opt = document.createElement('option');
        opt.value = i;
        opt.innerText = `${v.name} (${v.lang})`;
        select.appendChild(opt);
      });
    }
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices;
    }

    // मीडिया इनपुट
    function toggleMenu() {
      const m = document.getElementById('menuOverlay');
      m.style.display = m.style.display === 'flex' ? 'none' : 'flex';
    }
    function triggerFile(id) { toggleMenu(); document.getElementById(id).click(); }

    ['cameraInput', 'galleryInput', 'videoInput'].forEach(id => {
      document.getElementById(id).addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        currentMimeType = file.type;
        const reader = new FileReader();
        reader.onload = function(evt) {
          currentBase64 = evt.target.result.split(',')[1];
          document.getElementById('stagedContainer').style.display = 'flex';
          document.getElementById('stagedThumb').src = file.type.startsWith('video/') ? "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' fill='%2300f0ff' viewBox='0 0 24 24'><path d='M8 5v14l11-7z'/></svg>" : evt.target.result;
          document.getElementById('stagedText').innerText = file.name;
        };
        reader.readAsDataURL(file);
      });
    });

    function clearMedia() {
      currentBase64 = null; currentMimeType = null;
      document.getElementById('stagedContainer').style.display = 'none';
    }

    function appendChat(text, sender, tag = null) {
      const box = document.getElementById('chatBox');
      const msg = document.createElement('div');
      msg.className = `message ${sender}`;
      if(tag) {
        const t = document.createElement('div');
        t.className = 'core-tag';
        t.innerText = tag;
        msg.appendChild(t);
      }
      const s = document.createElement('div');
      s.innerText = text;
      msg.appendChild(s);
      box.appendChild(msg);
      box.scrollTop = box.scrollHeight;
      return s;
    }

    async function sendChat() {
      const inp = document.getElementById('userInput');
      const val = inp.value.trim();
      if(!val && !currentBase64) return;
      saveHistory(val);
      appendChat(val || "मीडिया विश्लेषण", 'user');
      inp.value = '';
      const media = currentBase64;
      const mime = currentMimeType;
      clearMedia();

      const load = appendChat("विचार कर रहा हूँ...", 'jarvis', currentMode.toUpperCase());
      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ message: val, image: media, mime_type: mime, mode: currentMode })
        });
        const data = await res.json();
        load.innerText = data.reply || "उत्तर प्राप्त हुआ।";
      } catch(e) {
        load.innerText = "सर्वर तैयार हो रहा है, कृपया पुनः प्रयास करें।";
      }
    }

    // ==========================================
    // रियल-टाइम वॉइस मोड (Full Duplex + Barge-in)
    // ==========================================
    function openVoiceMode() {
      isVoiceModalOpen = true;
      document.getElementById('voiceModal').style.display = 'flex';
      initSpeechRecognition();
    }

    function closeVoiceMode() {
      isVoiceModalOpen = false;
      document.getElementById('voiceModal').style.display = 'none';
      if(synth) synth.cancel();
      if(recognition) recognition.stop();
    }

    function initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if(!SpeechRecognition) {
        alert("आपका ब्राउज़र वॉइस पहचान का समर्थन नहीं करता। क्रोम का उपयोग करें।");
        return;
      }

      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'hi-IN'; // हिंदी व बहुभाषी सपोर्ट

      const orb = document.getElementById('voiceOrb');
      const status = document.getElementById('voiceStatus');
      const transcriptDiv = document.getElementById('voiceTranscript');

      recognition.onstart = () => {
        orb.className = "voice-orb listening";
        status.innerText = "सुन रहा हूँ... बोलिए";
      };

      recognition.onresult = (event) => {
        let interim = '';
        let final = '';

        // अगर AI बोल रहा है और यूज़र बोलने लगे (Barge-in / इंटरप्शन): AI को तुरंत चुप कराओ!
        if (synth.speaking) {
          synth.cancel();
          orb.className = "voice-orb listening";
        }

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        transcriptDiv.innerText = final || interim;

        if (final.trim().length > 1) {
          handleVoiceQuery(final.trim());
        }
      };

      recognition.onerror = () => {
        if(isVoiceModalOpen) try { recognition.start(); } catch(e){}
      };

      recognition.onend = () => {
        if(isVoiceModalOpen && !synth.speaking) {
          try { recognition.start(); } catch(e){}
        }
      };

      recognition.start();
    }

    async function handleVoiceQuery(text) {
      const orb = document.getElementById('voiceOrb');
      const status = document.getElementById('voiceStatus');
      
      status.innerText = "विचार कर रहा हूँ...";
      orb.className = "voice-orb";

      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ message: text, mode: "turbo" })
        });
        const data = await res.json();
        const reply = data.reply || "हाँ, बताइए।";
        speakResponse(reply);
      } catch(e) {
        speakResponse("माफ़ कीजिए, नेटवर्क में कुछ रुकावट आई।");
      }
    }

    function speakResponse(text) {
      if(!isVoiceModalOpen) return;
      synth.cancel();

      const utter = new SpeechSynthesisUtterance(text);
      const orb = document.getElementById('voiceOrb');
      const status = document.getElementById('voiceStatus');

      // चुनी गई आवाज़ लगाना
      const voices = synth.getVoices();
      const selIdx = document.getElementById('voiceSelect').value;
      if(voices[selIdx]) utter.voice = voices[selIdx];

      utter.rate = parseFloat(document.getElementById('voiceRate').value || 1.0);

      utter.onstart = () => {
        orb.className = "voice-orb speaking";
        status.innerText = "Jarvis बोल रहा है...";
      };

      utter.onend = () => {
        orb.className = "voice-orb listening";
        status.innerText = "सुन रहा हूँ... बोलिए";
        document.getElementById('voiceTranscript').innerText = "";
      };

      synth.speak(utter);
    }
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
