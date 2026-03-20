from flask import Flask, render_template_string, request, jsonify
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_na_jai_2026_final"

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

# UI ดีไซน์ใหม่: ส้ม-น้ำเงินเข้ม อ่านง่าย ไม่ปวดตา
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>นครนายก นาใจ 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:ital,wght@0,900;1,900&family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #050a14; color: white; font-family: 'Sarabun', sans-serif; }
        .font-kanit { font-family: 'Kanit', sans-serif; font-style: italic; }
        .bg-orange-main { background-color: #ea580c; }
        .border-orange-main { border-color: #ea580c; }
        .card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 1.5rem; }
        .tab-active { border-bottom: 4px solid #ea580c; color: #ea580c; font-weight: bold; }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center">

    <div class="mt-8 text-center mb-10">
        <h1 class="text-5xl font-kanit uppercase tracking-tighter">นครนายก <span class="text-[#ea580c]">นาใจ</span></h1>
        <p class="text-slate-400 mt-2 text-sm">Secret Buddy: สุ่มคนดวงซวยที่มึงต้องซื้อเสื้อให้</p>
    </div>

    <div class="w-full max-w-md">
        <!-- Tab Navigation -->
        <div class="flex mb-6 bg-[#0f172a] rounded-xl p-1">
            <a href="/" class="flex-1 py-3 text-center text-sm {{ 'tab-active' if not is_admin else '' }}">🎁 สุ่มคู่</a>
            <a href="/admin" class="flex-1 py-3 text-center text-sm {{ 'tab-active' if is_admin else '' }}">⚙️ จัดการแก๊ง</a>
        </div>

        <div class="card p-8 shadow-2xl">
            {% if not is_admin %}
                <div class="text-center">
                    <div class="text-5xl mb-4">👻</div>
                    <h2 class="text-lg font-bold mb-6 text-slate-200">มึงคือใครในกลุ่ม?</h2>
                    
                    <form action="/draw" method="POST">
                        <select name="user_name" class="w-full bg-[#1a2333] border border-slate-700 rounded-xl py-4 px-4 text-white text-lg mb-6 focus:outline-none focus:border-orange-500">
                            <option value="">-- เลือกชื่อตัวเอง --</option>
                            {% for name in names %}
                                <option value="{{ name }}">{{ name }}</option>
                            {% endfor %}
                        </select>
                        <button type="submit" class="w-full bg-orange-main hover:bg-orange-600 text-white font-bold py-4 rounded-xl text-xl transition-transform active:scale-95">
                            สุ่มเลยว้อย!
                        </button>
                    </form>
                </div>
            {% else %}
                <h2 class="text-xl font-kanit mb-4 text-[#ea580c] italic uppercase">Admin Panel</h2>
                <form action="/update_config" method="POST" class="space-y-6">
                    <div>
                        <label class="block text-sm font-bold text-slate-300 mb-2">รายชื่อเพื่อนทั้งหมด (ก๊อปวาง บรรทัดละคน):</label>
                        <textarea name="raw_names" rows="6" class="w-full bg-[#1a2333] border border-slate-700 rounded-xl p-4 text-white text-sm focus:outline-none focus:border-orange-500">{{ raw_names }}</textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-red-400 mb-2">คู่ห้าม (ห้ามสุ่มเจอกัน เช่น แฟน):</label>
                        <p class="text-[10px] text-slate-500 mb-2">* พิมพ์แบบ: ชื่อA,ชื่อB (1 คู่ต่อบรรทัด)</p>
                        <textarea name="raw_exclusions" rows="3" class="w-full bg-[#1a2333] border border-slate-700 rounded-xl p-4 text-white text-sm focus:outline-none">{{ raw_exclusions }}</textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-colors">
                        บันทึกข้อมูลทั้งหมด
                    </button>
                </form>
                <div class="mt-8">
                    <h3 class="text-sm font-bold text-slate-400 mb-4 italic">ประวัติการสุ่ม (ความลับสุดยอด):</h3>
                    <div class="max-h-40 overflow-y-auto space-y-2">
                        {% for giver, receiver in assignments.items() %}
                            <div class="text-xs bg-[#1a2333] p-2 rounded border border-slate-800">
                                <span class="text-orange-400">{{ giver }}</span> 👉 <span class="text-green-400">{{ receiver }}</span>
                            </div>
                        {% endfor %}
                    </div>
                    <a href="/clear" class="block text-center text-xs text-red-500 mt-6 underline" onclick="return confirm('จะลบประวัติสุ่มทั้งหมดจริงนะ?')">ล้างประวัติการสุ่มใหม่หมด</a>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Result Modal -->
    {% if result %}
    <div id="modal" class="fixed inset-0 bg-black/90 flex items-center justify-center p-4 z-50">
        <div class="bg-[#0f172a] border-2 border-orange-main p-10 rounded-[2.5rem] text-center w-full max-w-sm">
            <h2 class="text-slate-400 text-sm mb-2 uppercase font-bold">คนที่มึงจับได้คือ...</h2>
            <div class="text-5xl font-kanit text-white my-8 italic uppercase tracking-widest">{{ result }}</div>
            <button onclick="document.getElementById('modal').remove()" class="bg-orange-main w-full py-4 rounded-2xl font-bold text-lg shadow-lg">โอเค จำใส่สมองแล้ว</button>
        </div>
    </div>
    {% endif %}

</body>
</html>
"""

@app.route("/")
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=sorted(data["names"]), is_admin=False)

@app.route("/admin")
def admin():
    data = load_data()
    raw_names = "\n".join(data["names"])
    raw_ex = "\n".join([f"{a},{b}" for a, b in data.get("exclusions", [])])
    return render_template_string(HTML_TEMPLATE, names=data["names"], raw_names=raw_names, raw_exclusions=raw_ex, assignments=data["assignments"], is_admin=True)

@app.route("/update_config", methods=["POST"])
def update_config():
    data = load_data()
    # Bulk Update Names
    raw_names = request.form.get("raw_names", "")
    data["names"] = [n.strip() for n in raw_names.split("\n") if n.strip()]
    
    # Bulk Update Exclusions (Pairs that can't match)
    raw_ex = request.form.get("raw_exclusions", "")
    new_ex = []
    for line in raw_ex.split("\n"):
        if "," in line:
            pair = [p.strip() for p in line.split(",")]
            if len(pair) == 2: new_ex.append(pair)
    data["exclusions"] = new_ex
    
    save_data(data)
    return "<script>alert('บันทึกเรียบร้อย!'); window.location='/admin';</script>"

@app.route("/draw", methods=["POST"])
def draw():
    user_name = request.form.get("user_name")
    data = load_data()
    
    if not user_name:
        return "<script>alert('มึงลืมเลือกชื่อตัวเอง!'); window.location='/';</script>"

    # ถ้าสุ่มไปแล้ว ให้ค่าเดิม
    if user_name in data["assignments"]:
        return render_template_string(HTML_TEMPLATE, names=data["names"], is_admin=False, result=data["assignments"][user_name])

    # ตรรกะการสุ่ม
    already_assigned = list(data["assignments"].values())
    candidates = [n for n in data["names"] if n != user_name and n not in already_assigned]
    
    # กันแฟน (Exclusions)
    for a, b in data.get("exclusions", []):
        if user_name == a and b in candidates: candidates.remove(b)
        if user_name == b and a in candidates: candidates.remove(a)

    if not candidates:
        return "<script>alert('เกิดข้อผิดพลาด: ไม่มีคนเหลือให้มึงสุ่มแล้ว (หรือติดเงื่อนไขคู่ห้าม)'); window.location='/';</script>"

    final_choice = random.choice(candidates)
    data["assignments"][user_name] = final_choice
    save_data(data)
    
    return render_template_string(HTML_TEMPLATE, names=data["names"], is_admin=False, result=final_choice)

@app.route("/clear")
def clear():
    data = load_data()
    data["assignments"] = {}
    save_data(data)
    return "<script>alert('ล้างประวัติแล้ว สุ่มใหม่ได้เลย!'); window.location='/admin';</script>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))