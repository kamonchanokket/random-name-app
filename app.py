from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_na_jai_v6_fixed"

DATA_FILE = "data.json"
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl" # เปลี่ยนรหัสตรงนี้ได้ครับ

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
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
    <title>ทริป นครนายก นาใจ 2026 - Secret Buddy</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #020617; color: #f8fafc; }
        .glass-card { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .custom-shadow { box-shadow: 0 0 50px -12px rgba(249, 115, 22, 0.3); }
        .btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); transition: all 0.2s ease; }
        .btn-primary:hover { transform: translateY(-1px); }
        select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23ea580c'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 1rem center; background-size: 1.5em; }
    </style>
</head>
<body class="min-h-screen pb-12">
    <div class="max-w-md mx-auto p-4 pt-8">
        
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-3xl font-black text-white mb-1">นครนายก <span class="text-orange-500">นาใจ</span></h1>
            <p class="text-slate-500 text-xs italic">Secret Buddy เสื้อที่มึงไม่อยากใส่แต่ต้องใส่</p>
        </div>

        <!-- Nav -->
        <div class="flex justify-center mb-8 bg-slate-900/80 p-1 rounded-2xl border border-white/5">
            <a href="/" class="flex-1 text-center py-3 rounded-xl text-sm font-bold {{ 'bg-orange-600 text-white' if page == 'index' else 'text-slate-500' }}">🎁 สุ่มชื่อ</a>
            <a href="/admin" class="flex-1 text-center py-3 rounded-xl text-sm font-bold {{ 'bg-orange-600 text-white' if page == 'admin' or page == 'login' else 'text-slate-500' }}">⚙️ จัดการแก๊ง</a>
        </div>

        <div class="glass-card rounded-[2.5rem] p-8 shadow-2xl custom-shadow">
            
            {% if page == 'login' %}
                <form action="/admin_login" method="POST" class="text-center space-y-6">
                    <i data-lucide="lock" class="mx-auto text-orange-500 w-12 h-12"></i>
                    <h2 class="font-bold text-white">เฉพาะแอดมินเท่านั้น</h2>
                    <input type="password" name="pw" placeholder="ใส่รหัสผ่าน" class="w-full bg-slate-950 border border-slate-800 rounded-xl py-4 text-center text-white focus:border-orange-500 outline-none">
                    <button type="submit" class="w-full py-3 btn-primary rounded-xl font-bold text-white">เข้าสู่ระบบ</button>
                </form>

            {% elif page == 'admin' %}
                <div class="space-y-6">
                    <!-- Add Name ทีละคน -->
                    <div>
                        <h3 class="text-orange-400 text-xs font-black mb-3 uppercase tracking-widest">เพิ่มสมาชิกแก๊ง</h3>
                        <form action="/add_name" method="POST" class="flex gap-2">
                            <input type="text" name="new_name" placeholder="ชื่อเล่นเพื่อน..." class="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-white focus:border-orange-500 outline-none">
                            <button type="submit" class="bg-orange-600 px-4 rounded-xl font-bold text-white">+</button>
                        </form>
                    </div>

                    <!-- List of Names -->
                    <div class="flex flex-wrap gap-2">
                        {% for name in names %}
                        <div class="bg-slate-800/50 border border-white/5 px-3 py-1 rounded-lg text-xs flex items-center gap-2">
                            <span>{{ name }}</span>
                            <a href="/del_name/{{ name }}" class="text-rose-500 font-bold">×</a>
                        </div>
                        {% endfor %}
                    </div>

                    <!-- Exclusions -->
                    <div class="pt-4 border-t border-white/5">
                        <h3 class="text-rose-400 text-xs font-black mb-3 uppercase tracking-widest">คู่ห้าม (เช่น แฟนกัน)</h3>
                        <form action="/add_exclusion" method="POST" class="grid grid-cols-2 gap-2 mb-2">
                            <select name="p1" class="bg-slate-950 border border-slate-800 rounded-xl p-2 text-xs text-white">
                                {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                            </select>
                            <select name="p2" class="bg-slate-950 border border-slate-800 rounded-xl p-2 text-xs text-white">
                                {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                            </select>
                            <button type="submit" class="col-span-2 bg-slate-800 text-white py-2 rounded-xl text-[10px] font-bold">บันทึกคู่ห้าม</button>
                        </form>
                        {% for pair in exclusions %}
                        <div class="flex justify-between bg-rose-500/5 p-2 rounded text-[10px] border border-rose-500/10 mb-1">
                            <span>{{ pair[0] }} ❌ {{ pair[1] }}</span>
                            <a href="/del_exclusion/{{ loop.index0 }}" class="text-rose-500">ลบ</a>
                        </div>
                        {% endfor %}
                    </div>

                    <div class="pt-4 border-t border-white/5 text-center">
                        <a href="/logout" class="text-[10px] text-slate-500 underline">ออกจากระบบ</a>
                        <a href="/reset" class="block text-[10px] text-rose-500 mt-4" onclick="return confirm('ล้างข้อมูลสุ่มทั้งหมด?')">ล้างประวัติสุ่มใหม่หมด</a>
                    </div>
                </div>

            {% else %}
                <!-- User Draw -->
                <div class="text-center space-y-8">
                    <i data-lucide="ghost" class="mx-auto text-orange-400 w-16 h-16"></i>
                    <form action="/draw" method="POST" class="space-y-6">
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-orange-400 uppercase tracking-widest">มึงคือใครในแก๊ง?</label>
                            <select name="user_name" class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-5 text-xl font-bold text-white text-center outline-none">
                                <option value="">-- เลือกชื่อตัวเอง --</option>
                                {% for name in names | sort %}
                                    <option value="{{ name }}">{{ name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="w-full py-5 rounded-2xl font-black text-xl btn-primary text-white shadow-lg">สุ่มหาเหยื่อ!</button>
                    </form>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Result Modal -->
    {% if result %}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="glass-card w-full max-w-xs p-8 rounded-[2.5rem] border border-orange-500/30 text-center space-y-6">
            <p class="text-slate-400 text-[10px] font-black uppercase tracking-widest">เตรียมชุดให้เพื่อนคนนี้...</p>
            <h2 class="text-5xl font-black text-white py-2">{{ result }}</h2>
            <div class="p-4 bg-orange-500/10 rounded-2xl text-orange-300 text-[11px]">หาชุดที่มันเห็นแล้วต้องร้องไห้!</div>
            <button onclick="window.location='/'" class="text-slate-500 text-[10px] font-black uppercase tracking-widest">ตกลง</button>
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
    return render_template_string(HTML_TEMPLATE, names=data["names"], exclusions=data["exclusions"], page='admin')

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

# ฟังก์ชันเพิ่มชื่อทีละคน
@app.route("/add_name", methods=["POST"])
def add_name():
    name = request.form.get("new_name", "").strip()
    if not name: return redirect(url_for("admin"))
    data = load_data()
    if name not in data["names"]:
        data["names"].append(name)
        save_data(data)
    return redirect(url_for("admin"))

@app.route("/del_name/<name>")
def del_name(name):
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    if name in data["names"]:
        data["names"].remove(name)
        # ล้างข้อมูลสุ่มที่เกี่ยวข้องด้วยเพื่อป้องกัน Error
        data["assignments"] = {k: v for k, v in data["assignments"].items() if k != name and v != name}
        save_data(data)
    return redirect(url_for("admin"))

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
    if not user: return "<script>alert('เลือกชื่อก่อน!'); window.location='/';</script>"
    
    data = load_data()
    # ถ้าเคยสุ่มแล้ว ให้โชว์คนเดิม
    if user in data["assignments"]:
        return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=data["assignments"][user])

    # หาคนที่ยังไม่โดนเลือก
    assigned_receivers = list(data["assignments"].values())
    candidates = [n for n in data["names"] if n != user and n not in assigned_receivers]
    
    # กรองคู่ห้าม
    for p1, p2 in data["exclusions"]:
        if user == p1 and p2 in candidates: candidates.remove(p2)
        if user == p2 and p1 in candidates: candidates.remove(p1)

    if not candidates:
        return "<script>alert('ไม่มีใครเหลือให้สุ่มแล้ว หรือติดเงื่อนไขคู่ห้าม! ลองติดต่อแอดมิน'); window.location='/';</script>"

    target = random.choice(candidates)
    data["assignments"][user] = target
    save_data(data)
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target)

@app.route("/reset")
def reset():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    data["assignments"] = {}
    save_data(data)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)