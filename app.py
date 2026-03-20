from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_na_jai_2026_perfect_v10"

DATA_FILE = "data.json"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl" 

# ข้อมูลรายชื่อและไซส์เสื้อ 18 คน
INITIAL_MEMBERS = {
    "นิ๊ค": "40 - 42 นิ้ว",
    "พี่มิว": "44 - 46 นิ้ว",
    "เตอร์": "50 - 52 นิ้วมั้ง 3XL",
    "บ๊อบ": "50 - 52 นิ้วมั้ง 3XL",
    "แมน": "50 - 52 นิ้วมั้ง 3XL",
    "พิน": "40 - 42 นิ้ว",
    "มิ้ว": "40 นิ้ว",
    "วาย": "44-46",
    "แพร": "44-46",
    "เกรส": "40-42",
    "เหมี่ยว": "44 - 46 นิ้ว",
    "บอส": "44 - 46 นิ้ว",
    "นุ่น": "44-46",
    "จิน": "46-48",
    "อู๋": "44 - 46 นิ้ว",
    "สตางค์": "58-60 นิ้ว",
    "ออฟ": "62-64 นิ้ว",
    "กี้": "40 นิ้ว"
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except: 
            data = {"names": list(INITIAL_MEMBERS.keys()), "assignments": {}, "sizes": INITIAL_MEMBERS, "exclusions": []}
    else:
        data = {"names": list(INITIAL_MEMBERS.keys()), "assignments": {}, "sizes": INITIAL_MEMBERS, "exclusions": []}
        save_data(data)
    
    # ตรวจสอบฟิลด์ป้องกัน Error
    if "names" not in data: data["names"] = list(INITIAL_MEMBERS.keys())
    if "assignments" not in data: data["assignments"] = {}
    if "sizes" not in data: data["sizes"] = INITIAL_MEMBERS
    if "exclusions" not in data: data["exclusions"] = []
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>นครนายก นาใจ 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background: radial-gradient(circle at top right, #1e293b, #020617); color: #f8fafc; min-height: 100vh; }
        .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .btn-gradient { background: linear-gradient(135deg, #f97316 0%, #d946ef 100%); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .btn-gradient:hover { transform: translateY(-3px); box-shadow: 0 10px 20px -5px rgba(249, 115, 22, 0.5); }
        select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23f97316'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 1rem center; background-size: 1.2em; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-md mx-auto">
        <header class="text-center mb-10">
            <h1 class="text-4xl font-extrabold text-white mb-2">นครนายก <span class="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-pink-500">นาใจ</span></h1>
            <p class="text-slate-400 text-sm italic">"สุ่มหาเหยื่อ (พร้อมไซส์เสื้อ) ฉบับแอดมินไม่รู้โพย"</p>
        </header>

        <nav class="flex p-1.5 bg-slate-900/50 rounded-2xl border border-white/5 mb-8">
            <a href="{{ url_for('index') }}" class="flex-1 text-center py-3 rounded-xl text-sm font-semibold transition-all {{ 'bg-white/10 text-white' if page == 'index' else 'text-slate-500' }}">สุ่มหาเหยื่อ</a>
            <a href="{{ url_for('admin') }}" class="flex-1 text-center py-3 rounded-xl text-sm font-semibold transition-all {{ 'bg-white/10 text-white' if page in ['admin', 'login'] else 'text-slate-500' }}">แอดมิน</a>
        </nav>

        <main class="glass-card rounded-[2.5rem] p-8 relative">
            {% if page == 'login' %}
                <form action="{{ url_for('admin_login') }}" method="POST" class="space-y-4 py-4 text-center">
                    <i data-lucide="lock" class="text-orange-500 w-12 h-12 mx-auto mb-4"></i>
                    <h2 class="text-xl font-bold">แอดมินยืนยันตัวตน</h2>
                    <input type="password" name="pw" placeholder="รหัสผ่าน" class="w-full bg-slate-950/50 border border-slate-700 rounded-2xl py-4 px-6 text-center text-white outline-none focus:ring-2 ring-orange-500/50">
                    <button type="submit" class="w-full py-4 btn-gradient rounded-2xl font-bold text-white">เข้าสู่ระบบ</button>
                </form>
            {% elif page == 'admin' %}
                <div class="space-y-8">
                    <section class="text-center p-6 bg-orange-500/10 rounded-3xl border border-orange-500/20">
                         <p class="text-white text-sm">สุ่มไปแล้ว <span class="text-4xl font-black">{{ assignments|length }}</span> / {{ names|length }} คน</p>
                    </section>

                    <section class="p-5 bg-rose-500/5 rounded-3xl border border-rose-500/10">
                        <h3 class="text-rose-400 text-xs font-bold uppercase mb-4 flex items-center gap-2"><i data-lucide="shield-alert" class="w-4 h-4"></i> ล็อคคู่ห้ามสุ่มโดนกัน</h3>
                        <form action="{{ url_for('add_exclusion') }}" method="POST" class="space-y-3">
                            <div class="grid grid-cols-2 gap-2">
                                <select name="p1" class="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white">
                                    {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                                </select>
                                <select name="p2" class="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white">
                                    {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                                </select>
                            </div>
                            <button type="submit" class="w-full bg-rose-600 text-white py-3 rounded-xl text-xs font-bold uppercase">เพิ่มกฎห้ามคู่กัน</button>
                        </form>
                        <div class="mt-4 space-y-1">
                            {% for pair in exclusions %}
                            <div class="flex justify-between items-center bg-slate-900/50 p-2 rounded-xl text-[10px] text-slate-400">
                                <span>{{ pair[0] }} ❌ {{ pair[1] }}</span>
                                <a href="{{ url_for('del_exclusion', idx=loop.index0) }}" class="text-rose-500"><i data-lucide="x" class="w-3 h-3"></i></a>
                            </div>
                            {% endfor %}
                        </div>
                    </section>

                    <section>
                        <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">รายชื่อและ Size เสื้อทั้งหมด</label>
                        <div class="space-y-2 max-h-48 overflow-y-auto pr-2">
                            {% for name in names | sort %}
                            <div class="bg-slate-900/50 border border-white/5 p-3 rounded-xl flex justify-between items-center text-xs">
                                <span class="text-white">{{ name }}</span>
                                <span class="text-orange-400 font-bold">{{ sizes.get(name, '-') }}</span>
                            </div>
                            {% endfor %}
                        </div>
                    </section>

                    <footer class="pt-6 border-t border-white/10 text-center flex flex-col gap-4">
                        <a href="{{ url_for('logout') }}" class="text-slate-500 text-[10px] uppercase underline">LOGOUT</a>
                        <a href="{{ url_for('reset') }}" class="text-rose-500 text-[10px] font-bold uppercase underline" onclick="return confirm('ล้างข้อมูลใหม่หมด?')">ล้างประวัติ (Reset All)</a>
                    </footer>
                </div>
            {% else %}
                <div class="text-center py-4 space-y-8">
                    <form action="{{ url_for('draw') }}" method="POST" class="space-y-6">
                        <div class="space-y-4">
                            <label class="block text-xs font-bold text-orange-400 uppercase tracking-widest">เลือกชื่อของตัวเอง</label>
                            <select name="user_name" class="w-full bg-slate-950 border border-slate-800 rounded-3xl p-6 text-xl font-bold text-white text-center outline-none focus:ring-2 ring-orange-500/50" required>
                                <option value="">-- ใครเอ่ย? --</option>
                                {% for name in names | sort %}
                                    <option value="{{ name }}">{{ name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="w-full py-6 rounded-3xl font-black text-2xl btn-gradient text-white shadow-2xl">สุ่มหาเหยื่อ!</button>
                    </form>
                </div>
            {% endif %}
        </main>
    </div>

    {% if result %}
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/95 backdrop-blur-xl">
        <div class="glass-card w-full max-w-sm p-10 rounded-[3rem] border-2 border-orange-500/50 text-center space-y-8">
            <p class="text-slate-400 text-xs italic">เหยื่อที่มึงต้องไปหาชุดมาแกงคือ...</p>
            <div>
                <h2 class="text-6xl font-black text-white tracking-tighter">{{ result }}</h2>
                <div class="mt-4 px-6 py-2 bg-orange-500 text-white rounded-full font-bold text-lg inline-block">Size: {{ result_size }}</div>
            </div>
            <p class="text-slate-300 text-xs leading-relaxed italic">หาชุดที่ใส่แล้วโลกต้องจำ! ไซส์เสื้ออยู่ข้างบนแล้ว อย่าอ้างว่าซื้อผิดไซส์นะจ๊ะ 🤖✨</p>
            <button onclick="window.location='{{ url_for('index') }}'" class="w-full py-4 bg-slate-800 hover:bg-slate-700 rounded-2xl text-white text-xs font-bold uppercase">เก็บเป็นความลับสุดยอด</button>
        </div>
    </div>
    {% endif %}
    <script>lucide.createIcons();</script>
</body>
</html>
"""

@app.route("/")
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index')

@app.route("/admin")
def admin():
    if not session.get("is_admin"): return render_template_string(HTML_TEMPLATE, page='login')
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], sizes=data.get("sizes", {}), assignments=data.get("assignments", {}), exclusions=data.get("exclusions", []), page='admin')

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("pw") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("admin"))
    return "<script>alert('รหัสผิด!'); window.location='/admin';</script>"

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

@app.route("/add_exclusion", methods=["POST"])
def add_exclusion():
    p1, p2 = request.form.get("p1"), request.form.get("p2")
    if p1 == p2: return "<script>alert('ชื่อซ้ำกัน!'); window.location='/admin';</script>"
    data = load_data()
    data["exclusions"].append([p1, p2])
    save_data(data)
    return redirect(url_for("admin"))

@app.route("/del_exclusion/<int:idx>")
def del_exclusion(idx):
    data = load_data()
    if 0 <= idx < len(data["exclusions"]): data["exclusions"].pop(idx)
    save_data(data)
    return redirect(url_for("admin"))

@app.route("/draw", methods=["POST"])
def draw():
    user = request.form.get("user_name")
    data = load_data()
    
    if user in data["assignments"]:
        target = data["assignments"][user]
        return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target, result_size=data["sizes"].get(target, "ไม่ระบุ"))

    assigned_receivers = list(data["assignments"].values())
    candidates = [n for n in data["names"] if n != user and n not in assigned_receivers]
    
    # กรองคู่ห้าม (Exclusions)
    for p1, p2 in data.get("exclusions", []):
        if user == p1 and p2 in candidates: candidates.remove(p2)
        if user == p2 and p1 in candidates: candidates.remove(p1)

    if not candidates:
        return "<script>alert('ไม่มีใครเหลือให้สุ่มแล้ว หรือติดคู่ห้าม!'); window.location='/';</script>"

    target = random.choice(candidates)
    data["assignments"][user] = target
    save_data(data)
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target, result_size=data["sizes"].get(target, "ไม่ระบุ"))

@app.route("/reset")
def reset():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)