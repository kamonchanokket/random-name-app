from flask import Flask, request, jsonify, render_template_string
import random
import os

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"  # เปลี่ยนรหัสผ่านตรงนี้

# --- DATA STORAGE (In-Memory) ---
# หมายเหตุ: ข้อมูลจะหายถ้า Server Restart บน Render (Free Tier)
# หากต้องการเก็บถาวร ต้องต่อ Database เช่น PostgreSQL
db = {
    "all_names": ["ต้น", "เป็ด", "หมิว", "แนน", "บอย"], # รายชื่อเริ่มต้น (หรือแอดผ่านหน้า Admin)
    "remaining_pool": ["ต้น", "เป็ด", "หมิว", "แนน", "บอย"],
    "exclusions": [], # คู่ห้าม: [{"p1": "A", "p2": "B"}]
    "history": []     # ประวัติ: [{"drawer": "A", "drawn": "B", "time": "..."}]
}

# --- UI (HTML/Tailwind) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ทริป นครนายก นาใจ 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #020617; color: #f8fafc; }
        .glass-card { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }
    </style>
</head>
<body class="min-h-screen p-4 flex items-center justify-center">
    <div class="max-w-md w-full space-y-8">
        <div class="text-center">
            <h1 class="text-4xl font-black text-white">นครนายก นาใจ</h1>
            <p class="text-orange-500 font-bold tracking-widest uppercase text-xs mt-2">Secret Buddy 2026 (Server Mode)</p>
        </div>

        <div id="main-card" class="glass-card rounded-[2.5rem] p-8 shadow-2xl">
            <!-- สลับหน้าจอด้วย JS -->
            <div id="view-draw" class="space-y-6">
                <div class="space-y-2">
                    <label class="text-[10px] font-black text-orange-400 uppercase">คุณคือใคร?</label>
                    <select id="drawer-select" class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-white font-bold outline-none focus:border-orange-500 transition-all">
                        <option value="">-- เลือกชื่อ --</option>
                    </select>
                </div>
                <button onclick="draw()" class="w-full py-5 rounded-2xl font-black text-xl btn-primary text-white shadow-lg hover:scale-[1.02] transition-transform">
                    สุ่มคู่หู!
                </button>
            </div>

            <div id="view-result" class="hidden text-center space-y-6 py-4">
                <p class="text-slate-400 font-bold uppercase text-xs tracking-widest">คุณจับฉลากได้...</p>
                <h2 id="result-name" class="text-5xl font-black text-white animate-bounce">---</h2>
                <button onclick="location.reload()" class="text-slate-500 text-[10px] font-black uppercase tracking-widest">เสร็จสิ้น</button>
            </div>
        </div>

        <div class="text-center">
            <a href="/admin" class="text-slate-700 hover:text-orange-500 text-[10px] font-black uppercase">Admin Panel</a>
        </div>
    </div>

    <script>
        async function loadData() {
            const res = await fetch('/api/state');
            const data = await res.json();
            const select = document.getElementById('drawer-select');
            
            // กรองคนที่สุ่มไปแล้วออก
            const drawnUsers = data.history.map(h => h.drawer);
            const available = data.all_names.filter(n => !drawnUsers.includes(n));
            
            select.innerHTML = '<option value="">-- เลือกชื่อ --</option>' + 
                available.map(n => `<option value="${n}">${n}</option>`).join('');
        }

        async function draw() {
            const name = document.getElementById('drawer-select').value;
            if(!name) return alert("กรุณาเลือกชื่อ!");

            const res = await fetch('/api/draw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ drawer: name })
            });
            const data = await res.json();

            if(data.error) return alert(data.error);

            document.getElementById('view-draw').classList.add('hidden');
            document.getElementById('view-result').classList.remove('hidden');
            document.getElementById('result-name').innerText = data.drawn;
        }

        loadData();
    </script>
</body>
</html>
"""

# --- API ROUTES ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/state')
def get_state():
    return jsonify(db)

@app.route('/api/draw', methods=['POST'])
def perform_draw():
    data = request.json
    drawer = data.get('drawer')
    
    if any(h['drawer'] == drawer for h in db['history']):
        return jsonify({"error": "คุณสุ่มไปแล้ว!"}), 400

    # ตรวจสอบคู่ห้าม
    forbidden = [e['p1'] if e['p2'] == drawer else e['p2'] for e in db['exclusions'] if e['p1'] == drawer or e['p2'] == drawer]
    
    # กรองตัวเลือก: ไม่ใช่ตัวเอง และไม่ใช่คู่ห้าม
    options = [n for n in db['remaining_pool'] if n != drawer and n not in forbidden]
    
    if not options:
        return jsonify({"error": "ไม่เหลือชื่อที่สุ่มได้ (ติดเงื่อนไขคู่ห้าม)"}), 400

    result = random.choice(options)
    
    # อัปเดตข้อมูล
    db['remaining_pool'].remove(result)
    db['history'].append({
        "drawer": drawer,
        "drawn": result,
        "time": "Just now"
    })
    
    return jsonify({"drawn": result})

@app.route('/admin')
def admin_page():
    return """
    <h1>Admin Panel</h1>
    <p>ใส่รหัสผ่านเพื่อจัดการ (เร็วๆ นี้)</p>
    <a href="/">กลับหน้าหลัก</a>
    """

if __name__ == '__main__':
    # รันบน Render ต้องใช้ port จาก Environment
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)