from flask import Flask, render_template_string, request, jsonify, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakon_nayok_na_jai_secret"

# ไฟล์เก็บข้อมูล
DATA_FILE = "data.json"
ADMIN_PASSWORD = "1234"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"names": [], "assignments": {}, "pairs_drawn": []}
    return {"names": [], "assignments": {}, "pairs_drawn": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- UI TEMPLATE (ส้ม-น้ำเงินเข้ม แบบในรูป) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>นครนายก นาใจ</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:ital,wght@0,400;0,900;1,900&display=swap" rel="stylesheet">
    <style>
        body { background-color: #050a14; color: white; font-family: 'Kanit', sans-serif; }
        .neon-orange { color: #ea580c; text-shadow: 0 0 10px rgba(234, 88, 12, 0.5); }
        .bg-orange-custom { background-color: #ea580c; }
        .bg-dark-card { background-color: #0f172a; border: 1px solid #1e293b; }
        .font-heavy-italic { font-weight: 900; font-style: italic; }
        .tab-active { border-bottom: 4px solid #ea580c; color: #ea580c; }
    </style>
</head>
<body class="min-h-screen flex flex-col items-center p-4">

    <div class="mt-8 text-center">
        <div class="inline-block bg-[#1a1f2e] px-4 py-1 rounded-full border border-orange-900 mb-4">
            <span class="text-xs text-orange-500 font-bold uppercase tracking-widest">👕 NAKHON NAYOK POOL VILLA 2026</span>
        </div>
        <h1 class="text-5xl font-heavy-italic italic uppercase tracking-tighter">นครนายก <span class="neon-orange">นาใจ</span></h1>
        <p class="text-blue-300 italic text-sm mt-2 opacity-80">Secret Buddy เสื้อที่มึงไม่อยากใส่แต่ต้องใส่</p>
    </div>

    <div class="w-full max-w-md mt-10">
        <div class="flex mb-6 bg-[#0f172a] rounded-xl overflow-hidden p-1 shadow-xl">
            <a href="/" class="flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 {{ 'tab-active' if not is_admin else '' }}">
                🎁 จับคู่คนที่เราจะแกง
            </a>
            <a href="/admin" class="flex-1 py-3 text-sm font-bold flex items-center justify-center gap-2 {{ 'tab-active' if is_admin else '' }}">
                ⚙️ จัดการแก๊ง
            </a>
        </div>

        <div class="bg-dark-card rounded-3xl p-8 shadow-2xl">
            {% if not is_admin %}
                <div class="flex flex-col items-center">
                    <div class="w-24 h-24 bg-[#1a1f2e] rounded-2xl flex items-center justify-center mb-6 border border-orange-900/30">
                        <svg viewBox="0 0 24 24" class="w-12 h-12 text-orange-500" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 10h.01M15 10h.01M12 2a8 8 0 0 0-8 8v12l3-3 2.5 2.5L12 19l2.5 2.5L17 19l3 3V10a8 8 0 0 0-8-8z"/>
                        </svg>
                    </div>
                    <p class="text-blue-100 text-center text-sm mb-8 opacity-70">เลือกชื่อตัวเองจากรายการด้านล่าง<br>เพื่อดูว่ามึงต้องหาเสื้อให้ใครใส่!</p>
                    
                    <form action="/draw" method="POST" class="w-full">
                        <label class="block text-orange-500 font-heavy-italic text-xs mb-2 uppercase">มึงคือใครในแก๊ง?</label>
                        <select name="user_name" class="w-full bg-[#1a1f2e] border border-slate-700 rounded-xl py-4 px-4 text-center font-bold text-lg text-white mb-6">
                            <option value="">-- เลือกชื่อตัวเอง --</option>
                            {% for name in names %}
                                <option value="{{ name }}">{{ name }}</option>
                            {% endfor %}
                        </select>
                        <button type="submit" class="w-full bg-orange-custom hover:bg-orange-600 text-white font-heavy-italic py-4 rounded-xl text-xl shadow-lg transition-all active:scale-95">
                            สุ่มหาเหยื่อ!
                        </button>
                    </form>
                </div>
            {% else %}
                <h2 class="text-xl font-heavy-italic mb-4 text-orange-500 italic uppercase">Dashboard แอดมิน</h2>
                <form action="/update_names" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-blue-300 mb-1">รายชื่อเพื่อน (บรรทัดละชื่อ):</label>
                        <textarea name="raw_names" rows="6" class="w-full bg-[#1a1f2e] border border-slate-700 rounded-xl p-3 text-sm text-white">{{ raw_names }}</textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-lg text-sm">อัปเดตรายชื่อ</button>
                </form>
                <hr class="my-6 border-slate-800">
                <h3 class="font-bold text-orange-400 mb-2 italic">ประวัติการสุ่ม:</h3>
                <div class="text-xs space-y-1 opacity-80">
                    {% for giver, receiver in assignments.items() %}
                        <p>✅ {{ giver }} ➔ {{ receiver }}</p>
                    {% endfor %}
                </div>
            {% endif %}
        </div>
    </div>

    {% if result %}
    <div id="modal" class="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
        <div class="bg-dark-card border-2 border-orange-500 p-8 rounded-3xl text-center max-w-sm w-full">
            <h2 class="text-orange-500 font-heavy-italic text-2xl mb-4">มึงจับได้...</h2>
            <div class="text-4xl font-heavy-italic mb-6 text-white uppercase">{{ result }}</div>
            <button onclick="document.getElementById('modal').remove()" class="bg-orange-custom px-6 py-2 rounded-xl font-bold">ตกลง</button>
        </div>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], is_admin=False)

@app.route("/admin")
def admin():
    data = load_data()
    raw_names = "\n".join(data["names"])
    return render_template_string(HTML_TEMPLATE, names=data["names"], raw_names=raw_names, assignments=data["assignments"], is_admin=True)

@app.route("/update_names", methods=["POST"])
def update_names():
    new_names = [n.strip() for n in request.form.get("raw_names", "").split("\n") if n.strip()]
    data = load_data()
    data["names"] = new_names
    data["assignments"] = {}
    save_data(data)
    return "<script>alert('อัปเดตเรียบร้อย!'); window.location='/admin';</script>"

@app.route("/draw", methods=["POST"])
def draw():
    user_name = request.form.get("user_name")
    data = load_data()
    if not user_name: return "<script>alert('เลือกชื่อด้วยสิวะ!'); window.location='/';</script>"
    
    if user_name in data["assignments"]:
        return render_template_string(HTML_TEMPLATE, names=data["names"], is_admin=False, result=data["assignments"][user_name])

    available = [n for n in data["names"] if n != user_name and n not in data["assignments"].values()]
    if not available: return "<script>alert('ไม่มีใครเหลือแล้ว!'); window.location='/';</script>"

    target = random.choice(available)
    data["assignments"][user_name] = target
    save_data(data)
    return render_template_string(HTML_TEMPLATE, names=data["names"], is_admin=False, result=target)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))