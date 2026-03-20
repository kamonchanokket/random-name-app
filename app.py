from flask import Flask, request, jsonify, render_template_string
import random
import uuid

app = Flask(__name__)

# In-memory storage (ข้อมูลจะหายเมื่อ restart server)
# สำหรับใช้งานจริงแนะนำให้ใช้ Database
db = {
    "pool": [],        # รายชื่อที่ยังไม่ถูกสุ่ม
    "history": [],     # ประวัติ: [{"drawer": "A", "drawn": "B"}]
    "exclusions": {},  # คู่ห้าม: {"A": "B", "B": "A"}
    "admin_key": "mysecret" # รหัสสำหรับเข้าหน้า Admin
}

# ==========================================
# UI: USER PAGE
# ==========================================
USER_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Secret Draw 🎁</title>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;500&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Kanit', sans-serif; }
        body { 
            background: radial-gradient(circle, #1a1a2e 0%, #16213e 100%); 
            color: white; display: flex; justify-content: center; align-items: center; 
            height: 100vh; margin: 0;
        }
        .card {
            background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px);
            padding: 40px; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: center; width: 90%; max-width: 420px;
        }
        h2 { color: #e94560; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 3px; }
        p.desc { color: #999; font-size: 14px; margin-bottom: 30px; }
        input {
            width: 100%; padding: 15px; border-radius: 12px; border: none;
            background: rgba(255, 255, 255, 0.15); color: white; text-align: center;
            font-size: 18px; margin-bottom: 20px; outline: none; transition: 0.3s;
        }
        input:focus { background: rgba(255, 255, 255, 0.25); box-shadow: 0 0 10px #e94560; }
        button {
            width: 100%; padding: 15px; border: none; border-radius: 12px;
            font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s;
        }
        .btn-draw {
            background: #e94560; color: white; box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
        }
        .btn-draw:hover { transform: scale(1.02); background: #ff4d6d; }
        .result-box { display: none; margin-top: 20px; animation: fadeIn 0.8s; }
        .name-reveal { 
            font-size: 36px; color: #4ee; font-weight: bold; 
            text-shadow: 0 0 20px rgba(68, 238, 238, 0.6); margin: 25px 0;
        }
        .share-link {
            background: none; border: 1px solid #4ee; color: #4ee; font-size: 14px; margin-top: 15px;
        }
        .loader {
            display: none; border: 4px solid #f3f3f3; border-top: 4px solid #e94560;
            border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="card">
        <h2>Secret Santa 🎲</h2>
        <p class="desc">สุ่มชื่อลุ้นของขวัญ (ไม่มีสุ่มซ้ำ)</p>
        
        <div id="draw-form">
            <input type="text" id="username" placeholder="ใส่ชื่อเล่นของคุณที่นี่...">
            <button class="btn-draw" onclick="startDraw()">คลิกเพื่อเริ่มลุ้น!</button>
        </div>

        <div class="loader" id="loading"></div>

        <div id="result" class="result-box">
            <div style="color: #bbb;">คุณสุ่มได้...</div>
            <div class="name-reveal" id="drawnName">---</div>
            <p style="font-size: 12px; color: #666;">ห้ามบอกใครนะ! เป็นความลับ!</p>
            <button class="share-link" onclick="copyLink()">🔗 คัดลอกลิงก์ให้คนต่อไป</button>
        </div>
    </div>

    <script>
        async function startDraw() {
            const user = document.getElementById('username').value.trim();
            if(!user) { alert("กรุณาระบุชื่อของคุณก่อนสุ่มครับ"); return; }

            document.getElementById('draw-form').style.display = 'none';
            document.getElementById('loading').style.display = 'block';

            try {
                const res = await fetch('/api/draw', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ drawer: user })
                });
                const data = await res.json();
                
                setTimeout(() => {
                    document.getElementById('loading').style.display = 'none';
                    if(res.ok) {
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('drawnName').innerText = data.drawn;
                    } else {
                        alert(data.error);
                        document.getElementById('draw-form').style.display = 'block';
                    }
                }, 1500);
            } catch(e) { alert("เกิดข้อผิดพลาดในการเชื่อมต่อ"); }
        }

        function copyLink() {
            const el = document.createElement('textarea');
            el.value = window.location.origin;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            alert("คัดลอกลิงก์เรียบร้อย ส่งต่อได้เลย!");
        }
    </script>
</body>
</html>
"""

# ==========================================
# UI: ADMIN PAGE
# ==========================================
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        input, button { padding: 8px; margin: 4px; }
        .badge { background: #e94560; color: white; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Control Panel 🛡️</h1>
        
        <div class="section">
            <h3>1. เพิ่มรายชื่อ (Pool)</h3>
            <input type="text" id="newName" placeholder="ใส่ชื่อ...">
            <button onclick="addName()">เพิ่ม</button>
            <div style="margin-top:10px;">
                <strong>รายชื่อที่ยังเหลือ:</strong><br>
                <div id="poolDisplay">
                    {% for p in pool %} <span class="badge">{{p}}</span> {% endfor %}
                </div>
            </div>
        </div>

        <div class="section">
            <h3>2. ตั้งค่าคู่ห้าม (Exclusions)</h3>
            <small>* เช่น แฟนกันห้ามจับกันเอง</small><br>
            <input type="text" id="p1" placeholder="ชื่อคนที่ 1"> ห้ามจับได้ <input type="text" id="p2" placeholder="ชื่อคนที่ 2">
            <button onclick="addExclusion()">บันทึกเงื่อนไข</button>
            <ul>
                {% for k, v in exclusions.items() %}
                    <li>{{k}} ❌ {{v}}</li>
                {% endfor %}
            </ul>
        </div>

        <div class="section">
            <h3>3. ประวัติการสุ่ม (History)</h3>
            <table>
                <thead><tr><th>ผู้สุ่ม (Drawer)</th><th>คนที่สุ่มได้ (Drawn)</th></tr></thead>
                <tbody>
                    {% for h in history %}
                        <tr><td>{{h.drawer}}</td><td><strong>{{h.drawn}}</strong></td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const params = new URLSearchParams(window.location.search);
        const key = params.get('key');

        async function addName() {
            const name = document.getElementById('newName').value;
            await fetch('/api/admin/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ key: key, name: name })
            });
            location.reload();
        }

        async function addExclusion() {
            const p1 = document.getElementById('p1').value;
            const p2 = document.getElementById('p2').value;
            await fetch('/api/admin/exclude', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ key: key, p1: p1, p2: p2 })
            });
            location.reload();
        }
    </script>
</body>
</html>
"""

# ==========================================
# BACKEND LOGIC
# ==========================================

@app.route('/')
def home():
    return render_template_string(USER_HTML)

@app.route('/admin')
def admin():
    key = request.args.get('key')
    if key != db["admin_key"]:
        return "Unauthorized", 401
    return render_template_string(ADMIN_HTML, pool=db['pool'], history=db['history'], exclusions=db['exclusions'])

@app.route('/api/admin/add', methods=['POST'])
def admin_add():
    data = request.json
    if data.get('key') == db["admin_key"] and data.get('name'):
        name = data['name'].strip()
        if name not in db['pool']:
            db['pool'].append(name)
    return jsonify({"success": True})

@app.route('/api/admin/exclude', methods=['POST'])
def admin_exclude():
    data = request.json
    if data.get('key') == db["admin_key"]:
        p1, p2 = data.get('p1'), data.get('p2')
        if p1 and p2:
            db['exclusions'][p1] = p2
            db['exclusions'][p2] = p1 # ห้ามกันทั้งสองฝั่ง
    return jsonify({"success": True})

@app.route('/api/draw', methods=['POST'])
def draw_api():
    drawer = request.json.get('drawer', '').strip()
    if not drawer:
        return jsonify({"error": "กรุณาใส่ชื่อของคุณ"}), 400
    
    if not db['pool']:
        return jsonify({"error": "ขออภัย! รายชื่อในกล่องหมดแล้ว"}), 400

    # สร้างรายการตัวเลือกที่เป็นไปได้
    # เงื่อนไข: 1. ไม่ใช่ตัวเอง 2. ไม่ใช่คนที่เป็นคู่ห้าม (Exclusion)
    forbidden = db['exclusions'].get(drawer)
    choices = [name for name in db['pool'] if name != drawer and name != forbidden]

    if not choices:
        return jsonify({"error": "ไม่เหลือรายชื่อที่คุณสามารถสุ่มได้ (เนื่องจากติดเงื่อนไขคู่ห้าม หรือเหลือแค่ชื่อคุณ)"}), 400

    drawn = random.choice(choices)
    
    # ลบออกจาก Pool ทันที (ป้องกันการซ้ำ)
    db['pool'].remove(drawn)
    
    # บันทึกประวัติให้ Admin ดู
    db['history'].append({"drawer": drawer, "drawn": drawn})

    return jsonify({"drawn": drawn})

if __name__ == '__main__':
    app.run(debug=True)