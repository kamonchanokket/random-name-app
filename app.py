from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "nakhon_nayok_na_jai_secure_v4"

DATA_FILE = "data.json"
# --- แก้รหัสผ่าน Admin ตรงนี้ได้เลยครับ ---
ADMIN_PASSWORD = "123ปลาฉลามขึ้นบก" 

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
    <title>นครนายก นาใจ 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&family=Kanit:ital,wght@1,900&display=swap" rel="stylesheet">
    <style>
        body { background-color: #020617; color: #f8fafc; font-family: 'Sarabun', sans-serif; }
        .font-kanit { font-family: 'Kanit', sans-serif; }
        .card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 1rem; }
        .btn-orange { background-color: #ea580c; transition: all 0.2s; }
        .btn-orange:hover { background-color: #fb923c; transform: scale(1.02); }
        .tab-active { border-bottom: 3px solid #ea580c; color: #ea580c; font-weight: bold; }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center">

    <div class="mt-8 text-center mb-8">
        <h1 class="text-4xl font-kanit italic uppercase tracking-tighter">นครนายก <span class="text-[#ea580c]">นาใจ</span></h1>
        <p class="text-slate-400 text-xs mt-1 italic">Secret Buddy: เสื้อที่มึงไม่อยากใส่แต่ต้องใส่</p>
    </div>

    <div class="w-full max-w-md">
        <div class="flex mb-4 bg-[#0f172a] rounded-lg p-1 text-sm">
            <a href="/" class="flex-1 py-2 text-center {{ 'tab-active' if page == 'index' else '' }}">🎁 สุ่มชื่อ</a>
            <a href="/admin" class="flex-1 py-2 text-center {{ 'tab-active' if page == 'admin' else '' }}">⚙️ จัดการแก๊ง</a>
        </div>

        <div class="card p-6 shadow-xl">
            {% if page == 'login' %}
                <form action="/admin_login" method="POST" class="text-center">
                    <h2 class="text-orange-500 font-bold mb-4 uppercase italic">Admin Login</h2>
                    <input type="password" name="pw" placeholder="ใส่รหัสผ่านแอดมิน" class="w-full bg-[#1e293b] border border-slate-700 rounded-lg py-3 px-4 mb-4 text-center outline-none focus:border-orange-500">
                    <button type="submit" class="w-full btn-orange py-2 rounded font-bold">เข้าสู่ระบบ</button>
                </form>

            {% elif page == 'admin' %}
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-orange-500 font-bold italic uppercase text-lg">Admin Panel</h2>
                    <a href="/logout" class="text-[10px] text-slate-500 underline italic">ออกจากระบบ</a>
                </div>
                
                <form action="/update_names" method="POST" class="mb-8">
                    <label class="block text-[10px] text-slate-400 mb-1 font-bold uppercase">รายชื่อเพื่อน (ก๊อปวาง บรรทัดละคน):</label>
                    <textarea name="raw_names" rows="5" class="w-full bg-[#1e293b] border border-slate-700 rounded-lg p-3 text-sm mb-2" placeholder="ชื่อเพื่อน1&#10;ชื่อเพื่อน2">{{ raw_names }}</textarea>
                    <button type="submit" class="w-full bg-blue-600 py-2 rounded font-bold text-xs uppercase">บันทึกรายชื่อ</button>
                </form>

                <div class="border-t border-slate-800 pt-4 mb-6">
                    <label class="block text-[10px] text-red-400 mb-2 font-bold uppercase">เพิ่มคู่ห้าม (แฟนกัน):</label>
                    <form action="/add_exclusion" method="POST" class="flex gap-2 mb-4">
                        <select name="p1" class="flex-1 bg-[#1e293b] border border-slate-700 rounded p-1 text-xs">
                            {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                        </select>
                        <span class="pt-1 text-xs">❌</span>
                        <select name="p2" class="flex-1 bg-[#1e293b] border border-slate-700 rounded p-1 text-xs">
                            {% for name in names | sort %}<option value="{{ name }}">{{ name }}</option>{% endfor %}
                        </select>
                        <button type="submit" class="bg-red-600 px-3 rounded font-bold">+</button>
                    </form>

                    <div class="space-y-1">
                        {% for pair in exclusions %}
                        <div class="text-[11px] bg-[#1a2333] p-2 rounded flex justify-between items-center border border-slate-800">
                            <span>{{ pair[0] }} 💔 {{ pair[1] }}</span>
                            <a href="/del_exclusion/{{ loop.index0 }}" class="text-red-500 font-bold px-2">ลบ</a>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="border-t border-slate-800 pt-4">
                     <h3 class="text-[10px] font-bold text-slate-500 mb-2 italic">ประวัติการสุ่ม:</h3>
                     <div class="max-h-32 overflow-y-auto text-[10px] space-y-1 opacity-70">
                        {% for giver, receiver in assignments.items() %}
                            <div>{{ giver }} -> {{ receiver }}</div>
                        {% endfor %}
                     </div>
                </div>
                
                <a href="/reset" class="block text-center text-[10px] text-slate-600 mt-6 underline" onclick="return confirm('ลบประวัติสุ่มทั้งหมด?')">ล้างประวัติการสุ่มใหม่หมด</a>

            {% else %}
                <form action="/draw" method="POST" class="text-center">
                    <p class="mb-4 text-slate-300 text-sm">มึงคือใครในกลุ่มนี้?</p>
                    <select name="user_name" class="w-full bg-[#1e293b] border border-slate-700 rounded-lg py-3 px-4 mb-6 focus:ring-2 focus:ring-orange-500 outline-none text-lg">
                        <option value="">-- เลือกชื่อตัวเอง --</option>
                        {% for name in names | sort %}
                            <option value="{{ name }}">{{ name }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit" class="w-full btn-orange py-4 rounded-xl font-bold text-xl shadow-lg transition-transform active:scale-95">สุ่มหาเหยื่อ!</button>
                </form>
            {% endif %}
        </div>
    </div>

    {% if result %}
    <div id="modal" class="fixed inset-0 bg-black/95 flex items-center justify-center p-4 z-50">
        <div class="bg-[#0f172a] border-2 border-orange-500 p-8 rounded-2xl text-center w-full max-w-xs shadow-2xl">
            <h2 class="text-slate-400 text-[10px] mb-2 font-bold uppercase tracking-widest">มึงสุ่มได้...</h2>
            <div class="text-4xl font-kanit text-white my-8 italic uppercase tracking-tighter">{{ result }}</div>
            <button onclick="document.getElementById('modal').remove()" class="btn-orange w-full py-3 rounded-xl font-bold text-lg">จำใส่สมองไว้!</button>
        </div>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], page='index')

@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return render_template_string(HTML_TEMPLATE, page='login')
    data = load_data()
    return render_template_string(HTML_TEMPLATE, names=data["names"], raw_names="\\n".join(data["names"]), exclusions=data["exclusions"], assignments=data["assignments"], page='admin')

@app.route("/admin_login", methods=["POST"])
def admin_login():
    if request.form.get("pw") == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("admin"))
    return "<script>alert('รหัสผิดว้อย!'); window.location='/admin';</script>"

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

@app.route("/update_names", methods=["POST"])
def update_names():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    data["names"] = [n.strip() for n in request.form.get("raw_names", "").split("\\n") if n.strip()]
    save_data(data)
    return "<script>alert('บันทึกเรียบร้อย!'); window.location='/admin';</script>"

@app.route("/add_exclusion", methods=["POST"])
def add_exclusion():
    if not session.get("is_admin"): return redirect(url_for("admin"))
    p1, p2 = request.form.get("p1"), request.form.get("p2")
    if not p1 or not p2 or p1 == p2: return "<script>alert('เลือกชื่อให้มันถูก!'); window.location='/admin';</script>"
    data = load_data()
    data["exclusions"].append([p1, p2])
    save_data(data)
    return redirect(url_for("admin"))

@app.route("/del_exclusion/<int:idx>")
def del_exclusion(idx):
    if not session.get("is_admin"): return redirect(url_for("admin"))
    data = load_data()
    if 0 <= idx < len(data["exclusions"]): data["exclusions"].pop(idx)
    save_data(data)
    return redirect(url_for("admin"))

@app.route("/draw", methods=["POST"])
def draw():
    user = request.form.get("user_name")
    data = load_data()
    if not user: return "<script>alert('เลือกชื่อก่อนสิ!'); window.location='/';</script>"
    
    if user in data["assignments"]:
        return render_template_string(HTML_TEMPLATE, names=data["names"], page='index', result=data["assignments"][user])

    assigned = list(data["assignments"].values())
    candidates = [n for n in data["names"] if n != user and n not in assigned]
    
    for pair in data["exclusions"]:
        if user == pair[0] and pair[1] in candidates: candidates.remove(pair[1])
        if user == pair[1] and pair[0] in candidates: candidates.remove(pair[0])

    if not candidates: 
        return "<script>alert('ไม่มีใครให้สุ่มแล้ว (หรือติดเงื่อนไขคู่ห้าม)!'); window.location='/';</script>"

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
    return "<script>alert('ล้างประวัติแล้ว!'); window.location='/admin';</script>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))