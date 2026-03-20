from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_na_jai_glass_v5"

DATA_FILE = "data.json"
# --- รหัสผ่าน Admin ---
ADMIN_PASSWORD = "qwertyuiop[]asdfghjkl"[cite: 2]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"names": [], "assignments": {}, "exclusions": []}[cite: 2]

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)[cite: 2]

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
        body { font-family: 'Kanit', sans-serif; background-color: #020617; color: #f8fafc; overflow-x: hidden; }
        .glass-card { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .custom-shadow { box-shadow: 0 0 50px -12px rgba(249, 115, 22, 0.3); }
        .btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); transition: all 0.3s ease; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -10px rgba(249, 115, 22, 0.5); }
        select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23ea580c'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 1rem center; background-size: 1.5em; }
    </style>
</head>
<body class="min-h-screen pb-12">
    <div id="app" class="max-w-md mx-auto p-4 pt-8">
        
        <!-- Header Section -->
        <div class="text-center mb-8">
            <div class="inline-flex items-center space-x-2 px-3 py-1 bg-orange-500/10 rounded-full border border-orange-500/20 mb-4">
                <i data-lucide="shirt" class="w-3 h-3 text-orange-400"></i>
                <span class="text-[10px] font-bold text-orange-400 uppercase tracking-widest">Nakhon Nayok Pool Villa 2026</span>
            </div>
            <h1 class="text-3xl font-black tracking-tight text-white mb-1">นครนายก นาใจ</h1>
            <p class="text-slate-500 text-sm font-medium italic underline decoration-orange-500/30">Secret Buddy เสื้อที่มึงไม่อยากใส่แต่ต้องใส่</p>
        </div>

        <!-- Navigation Tabs -->
        <div class="flex justify-center mb-8">
            <div class="bg-slate-900/80 p-1 rounded-2xl border border-white/5 flex shadow-2xl w-full text-sm font-bold">
                <a href="/" class="flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-xl transition-all {{ 'bg-orange-600 text-white shadow-lg' if page == 'index' else 'text-slate-500 hover:text-slate-300' }}">
                    <i data-lucide="gift" class="w-4 h-4"></i>
                    <span>จับคู่คนที่จะแกง</span>
                </a>
                <a href="/admin" class="flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-xl transition-all {{ 'bg-orange-600 text-white shadow-lg' if page == 'admin' or page == 'login' else 'text-slate-500 hover:text-slate-300' }}">
                    <i data-lucide="settings" class="w-4 h-4"></i>
                    <span>จัดการแก๊ง</span>
                </a>
            </div>
        </div>

        <!-- Main Content -->
        <div class="glass-card rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden custom-shadow">
            
            {% if page == 'login' %}
                <div class="text-center space-y-6">
                    <div class="w-16 h-16 bg-orange-600/20 rounded-2xl flex items-center justify-center mx-auto border border-orange-500/40">
                        <i data-lucide="lock" class="text-orange-400 w-8 h-8"></i>
                    </div>
                    <div>
                        <h4 class="font-black text-white text-lg tracking-tight">เฉพาะแอดมินเท่านั้น</h4>
                        <p class="text-slate-500 text-[10px]">ใส่รหัสผ่านเพื่อเข้าสู่ระบบจัดการแก๊ง</p>
                    </div>
                    <form action="/admin_login" method="POST" class="space-y-4">
                        <input type="password" name="pw" placeholder="••••" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-4 text-center text-xl tracking-[0.5em] text-white focus:outline-none focus:border-orange-500">
                        <button type="submit" class="w-full py-3 btn-primary rounded-xl text-[10px] font-black text-white uppercase tracking-widest">ตกลง</button>
                    </form>
                </div>

            {% elif page == 'admin' %}
                <div class="space-y-6">
                    <div class="flex items-center justify-between">
                        <h3 class="font-black text-orange-400 uppercase text-xs tracking-widest">Admin Control</h3>
                        <a href="/logout" class="text-[9px] text-slate-500 underline uppercase font-bold">Logout</a>
                    </div>
                    
                    <form action="/update_names" method="POST" class="space-y-3">
                        <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">รายชื่อเพื่อน (บรรทัดละคน)</label>
                        <textarea name="raw_names" rows="5" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-orange-500" placeholder="ชื่อเพื่อน 1&#10;ชื่อเพื่อน 2">{{ raw_names }}</textarea>
                        <button type="submit" class="w-full bg-orange-600 py-3 rounded-xl text-xs font-bold text-white hover:bg-orange-500 transition-colors">อัปเดตรายชื่อ</button>
                    </form>

                    <div class="pt-4 border-t border-white/5">
                        <h3 class="font-black text-rose-400 mb-4 uppercase text-xs tracking-widest">คู่ห้ามสุ่มเจอกัน (แฟนกัน)</h3>
                        <form action="/add_exclusion" method="POST" class="space-y-3">
                            <div class="grid grid-cols-2 gap-2">
                                <select name="p1" class="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white">
                                    {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                                </select>
                                <select name="p2" class="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white">
                                    {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                                </select>
                            </div>
                            <button type="submit" class="w-full bg-slate-800 border border-white/5 text-slate-300 py-3 rounded-xl font-bold text-[10px] uppercase hover:bg-slate-700">เพิ่มคู่ห้าม</button>
                        </form>
                        <div class="mt-4 space-y-2">
                            {% for pair in exclusions %}
                            <div class="flex justify-between items-center bg-rose-500/5 border border-rose-500/10 p-2 rounded-lg text-[10px]">
                                <span class="text-rose-300">{{ pair[0] }} ❌ {{ pair[1] }}</span>
                                <a href="/del_exclusion/{{ loop.index0 }}" class="text-rose-500 font-bold uppercase">ลบ</a>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="pt-4 border-t border-white/5">
                        <h3 class="font-black text-emerald-400 mb-4 uppercase text-xs tracking-widest">ประวัติการสุ่ม (ความลับ)</h3>
                        <div class="space-y-2">
                            {% for giver, receiver in assignments.items() %}
                            <div class="bg-slate-900/50 p-3 rounded-xl border border-white/5 flex justify-between items-center text-[10px]">
                                <span><b class="text-white">{{ giver }}</b> สุ่มได้ <b class="text-orange-400">{{ receiver }}</b></span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    <a href="/reset" class="block text-center text-[9px] text-rose-500 font-bold uppercase tracking-widest mt-4" onclick="return confirm('ลบประวัติสุ่มทั้งหมด?')">ล้างข้อมูลสุ่มใหม่หมด</a>
                </div>

            {% else %}
                <div id="draw-initial" class="space-y-8">
                    <div class="text-center space-y-4">
                        <div class="w-20 h-20 bg-orange-600/10 rounded-3xl flex items-center justify-center mx-auto border border-orange-500/20">
                            <i data-lucide="ghost" class="text-orange-400 w-10 h-10"></i>
                        </div>
                        <p class="text-slate-400 text-xs font-medium px-4 leading-relaxed">เลือกชื่อตัวเองจากรายการด้านล่าง<br>เพื่อดูว่ามึงต้องหาเสื้อให้ใครใส่!</p>
                    </div>

                    <form action="/draw" method="POST" class="space-y-6">
                        <div class="space-y-2">
                            <label class="text-[10px] font-black text-orange-400 uppercase tracking-widest ml-1">มึงคือใครในแก๊ง?</label>
                            <select name="user_name" class="w-full bg-slate-950/50 border border-slate-800 rounded-2xl px-5 py-5 focus:outline-none focus:border-orange-500 transition-all text-center text-xl font-bold text-white shadow-inner cursor-pointer">
                                <option value="">-- เลือกชื่อตัวเอง --</option>
                                {% for name in names | sort %}
                                    <option value="{{ name }}">{{ name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <button type="submit" class="w-full py-5 rounded-2xl font-black text-xl btn-primary text-white transition-all">
                            สุ่มหาเหยื่อ!
                        </button>
                    </form>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Result Modal (แสดงเมื่อสุ่มสำเร็จ) -->
    {% if result %}
    <div id="modal-result" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/80 backdrop-blur-md"></div>
        <div class="glass-card w-full max-w-xs p-8 rounded-[2.5rem] border border-orange-500/30 relative text-center space-y-8 animate-in fade-in zoom-in duration-300">
            <div class="relative py-4">
                <div class="absolute inset-0 bg-orange-500/10 blur-3xl rounded-full scale-125"></div>
                <div class="relative">
                    <p class="text-slate-400 mb-4 font-black uppercase tracking-[0.2em] text-[10px]">เตรียมชุดให้เพื่อนคนนี้...</p>
                    <h2 class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-orange-200 to-white py-2">{{ result }}</h2>
                </div>
            </div>
            <div class="p-4 bg-orange-500/5 border border-orange-500/10 rounded-2xl">
                <p class="text-orange-300/80 text-[11px] font-medium leading-relaxed">มึงไปหาชุดมาให้เพื่อนคนนี้ใส่ด่วน!<br>คัดแบบที่เห็นแล้วต้องร้องไห้ แต่ต้องใส่ลงสระ!</p>
            </div>
            <button onclick="window.location='/'" class="text-slate-600 text-[10px] font-black hover:text-slate-400 uppercase tracking-[0.2em] transition-colors">จำใส่สมองแล้ว</button>
        </div>
    </div>
    {% endif %}

    <script>
        lucide.createIcons();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index')[cite: 2]

@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return render_template_string(HTML_TEMPLATE, page='login')[cite: 2]
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], raw_names="\\n".join(data["names"]), exclusions=data["exclusions"], assignments=data["assignments"], page='admin')[cite: 2]

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("pw") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("admin"))[cite: 2]
    return "<script>alert('รหัสผ่านไม่ถูกต้อง!'); window.location='/admin';</script>"[cite: 2]

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))[cite: 2]

@app.route("/update_names", methods=["POST"])
def update_names():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    data["names"] = [n.strip() for n in request.form.get("raw_names", "").split("\\n") if n.strip()][cite: 2]
    save_data(data)
    return "<script>alert('บันทึกรายชื่อเรียบร้อย!'); window.location='/admin';</script>"

@app.route("/add_exclusion", methods=["POST"])
def add_exclusion():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    p1, p2 = request.form.get("p1"), request.form.get("p2")
    if not p1 or not p2 or p1 == p2: return "<script>alert('กรุณาเลือกชื่อที่แตกต่างกัน!'); window.location='/admin';</script>"[cite: 2]
    data = load_data()
    data["exclusions"].append([p1, p2])[cite: 2]
    save_data(data)
    return redirect(url_for("admin"))[cite: 2]

@app.route("/del_exclusion/<int:idx>")
def del_exclusion(idx):
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    if 0 <= idx < len(data["exclusions"]): data["exclusions"].pop(idx)[cite: 2]
    save_data(data)
    return redirect(url_for("admin"))[cite: 2]

@app.route("/draw", methods=["POST"])
def draw():
    user = request.form.get("user_name")
    data = load_data()
    if not user: return "<script>alert('เลือกชื่อมึงก่อนสิเพื่อน!'); window.location='/';</script>"[cite: 2]
    
    if user in data["assignments"]:
        return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=data["assignments"][user])[cite: 2]

    assigned = list(data["assignments"].values())
    candidates = [n for n in data["names"] if n != user and n not in assigned][cite: 2]
    
    for pair in data["exclusions"]:
        if user == pair[0] and pair[1] in candidates: candidates.remove(pair[1])[cite: 2]
        if user == pair[1] and pair[0] in candidates: candidates.remove(pair[0])[cite: 2]

    if not candidates: 
        return "<script>alert('สุ่มไม่ได้! ไม่เหลือคนให้สุ่มแล้วหรือติดเงื่อนไขคู่ห้าม'); window.location='/';</script>"[cite: 2]

    target = random.choice(candidates)[cite: 2]
    data["assignments"][user] = target[cite: 2]
    save_data(data)
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=target)[cite: 2]

@app.route("/reset")
def reset():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    data["assignments"] = {}[cite: 2]
    save_data(data)
    return "<script>alert('ล้างข้อมูลเรียบร้อย!'); window.location='/admin';</script>"[cite: 2]

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))[cite: 2]