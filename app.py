from flask import Flask, render_template_string, request, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakon_nayok_na_jai_2026"

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"names": [], "assignments": {}, "exclusions": []}
    return {"names": [], "assignments": {}, "exclusions": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
    </div>

    <div class="w-full max-w-md mt-10">
        <div class="flex mb-6 bg-[#0f172a] rounded-xl overflow-hidden p-1 shadow-xl">
            <a href="/" class="flex-1 py-3 text-sm font-bold text-center {{ 'tab-active' if not is_admin else '' }}">🎁 จับคู่คนที่จะแกง</a>
            <a href="/admin" class="flex-1 py-3 text-sm font-bold text-center {{ 'tab-active' if is_admin else '' }}">⚙️ จัดการแก๊ง</a>
        </div>

        <div class="bg-dark-card rounded-3xl p-8 shadow-2xl">
            {% if not is_admin %}
                <div class="flex flex-col items-center">
                    <div class="w-20 h-20 bg-[#1a1f2e] rounded-2xl flex items-center justify-center mb-6 border border-orange-900/30 text-orange-500 text-4xl">👻</div>
                    <form action="/draw" methods="POST" class="w-full">
                        <label class="block text-orange-500 font-heavy-italic text-xs mb-2 uppercase italic">มึงคือใครในแก๊ง?</label>
                        <select name="user_name" class="w-full bg-[#1a1f2e] border border-slate-700 rounded-xl py-4 px-4 font-bold text-white mb-6">
                            <option value="">-- เลือกชื่อตัวเอง --</option>
                            {% for name in names %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                        </select>
                        <button type="submit" class="w-full bg-orange-custom hover:bg-orange-600 text-white font-heavy-italic py-4 rounded-xl text-xl transition-all">สุ่มหาเหยื่อ!</button>
                    </form>
                </div>
            {% else %}
                <h2 class="text-xl font-heavy-italic mb-4 text-orange-500 uppercase">Admin Dashboard</h2>
                <form action="/update_all" methods="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-blue-300 mb-1">รายชื่อเพื่อน (บรรทัดละชื่อ):</label>
                        <textarea name="raw_names" rows="4" class="w-full bg-[#1a1f2e] border border-slate-700 rounded-xl p-3 text-sm text-white">{{ raw_names }}</textarea>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-red-400 mb-1">คู่ห้ามสุ่มเจอกัน (เช่น A,B หนึ่งคู่ต่อบรรทัด):</label>
                        <textarea name="raw_exclusions" rows="3" class="w-full bg-[#1a1f2e] border border-slate-700 rounded-xl p-3 text-sm text-white" placeholder="แอดมิน,แฟนแอดมิน">{{ raw_exclusions }}</textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-lg text-sm">อัปเดตข้อมูลทั้งหมด</button>
                    <a href="/reset" class="block text-center text-xs text-red-500 underline mt-2">ล้างประวัติการสุ่มทั้งหมด</a>
                </form>
            {% endif %}
        </div>
    </div>

    {% if result %}
    <div id="modal" class="fixed inset-0 bg-black/90 flex items-center justify-center p-4 z-50">
        <div class="bg-dark-card border-2 border-orange-500 p-10 rounded-3xl text-center max-w-sm w-full">
            <h2 class="text-orange-500 font-heavy-italic text-xl mb-2">เหยื่อของมึงคือ...</h2>
            <div class="text-5xl font-heavy-italic mb-8 text-white uppercase italic tracking-tighter">{{ result }}</div>
            <button onclick="document.getElementById('modal').remove()" class="bg-orange-custom w-full py-3 rounded-xl font-bold">จำใส่สมองไว้!</button>
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
    raw_exclusions = "\n".join([f"{a},{b}" for a, b in data.get("exclusions", [])])
    return render_template_string(HTML_TEMPLATE, names=data["names"], raw_names=raw_names, raw_exclusions=raw_exclusions, assignments=data["assignments"], is_admin=True)

@app.route("/update_all", methods=["POST"])
def update_all():
    data = load_data()
    data["names"] = [n.strip() for n in request.form.get("raw_names", "").split("\n") if n.strip()]
    
    exclusions = []
    for line in request.form.get("raw_exclusions", "").split("\n"):
        if "," in line:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 2: exclusions.append(parts)
    data["exclusions"] = exclusions
    save_data(data)
    return "<script>alert('อัปเดตเรียบร้อย!'); window.location='/admin';</script>"

@app.route("/draw", methods=["POST"])
def draw():
    user_name = request.form.get("user_name")
    data = load_data()
    if not user_name: return "<script>alert('เลือกชื่อก่อน!'); window.location='/';</script>"
    
    if user_name in data["assignments"]:
        return render_template_string(HTML_TEMPLATE, names=data["names"], is_admin=False, result=data["assignments"][user_name])

    # กรองคนที่ไม่ใช่ตัวเอง และ ไม่ใช่คนที่สุ่มไปแล้ว
    already_drawn = data["assignments"].values()
    candidates = [n for n in data["names"] if n != user_name and n not in already_drawn]
    
    # กรอง "คู่ห้าม" (แฟน)
    for a, b in data.get("exclusions", []):
        if user_name == a and b in candidates: candidates.remove(b)
        if user_name == b and a in candidates: candidates.remove(a)

    if not candidates:
        return "<script>alert('ไม่มีใครให้มึงแกงแล้ว หรือติดเงื่อนไขคู่ห้าม!'); window.location='/';</script>"

    target = random.choice(candidates)
    data["assignments"][user_name] = target
    save_data(data)
    return render_template_string(HTML_TEMPLATE, names=data["names"], is_admin=False, result=target)

@app.route("/reset")
def reset():
    data = load_data()
    data["assignments"] = {}
    save_data(data)
    return "<script>alert('ล้างประวัติการสุ่มแล้ว!'); window.location='/admin';</script>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))