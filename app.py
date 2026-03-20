from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

# ฐานข้อมูลจำลอง (In-memory) 
# หมายเหตุ: ข้อมูลจะหายถ้า Restart Server หากใช้จริงแนะนำให้เชื่อม SQLite หรือ Database อื่นๆ
db = {
    "pool": [],      # รายชื่อที่ยังเหลือให้สุ่ม
    "history": []    # ประวัติการสุ่ม [{'drawer': 'A', 'drawn': 'B'}]
}

# รหัสลับสำหรับ Admin ในการดูประวัติ
ADMIN_SECRET = "mysecret" 

# ==========================================
# Frontend Templates (HTML/CSS/JS)
# ==========================================

USER_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ลุ้นรายชื่อผู้โชคดี!</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        input { padding: 10px; width: 80%; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; color: white; font-weight: bold; }
        .btn-draw { background-color: #28a745; }
        .btn-share { background-color: #007bff; display: none; margin-top: 15px; width: 100%;}
        #result { margin-top: 20px; font-size: 24px; font-weight: bold; color: #d9534f; }
    </style>
</head>
<body>
    <div class="container">
        <h2>ระบบสุ่มชื่อ 🎲</h2>
        <div id="draw-section">
            <p>กรุณากรอกชื่อของคุณ (ผู้สุ่ม)</p>
            <input type="text" id="drawerName" placeholder="ชื่อของคุณ...">
            <br>
            <button class="btn-draw" onclick="drawName()">สุ่มเลย!</button>
        </div>
        
        <div id="result"></div>
        <button id="shareBtn" class="btn-share" onclick="shareLink()">🔗 คัดลอกลิงก์ส่งให้คนต่อไป</button>
    </div>

    <script>
        async function drawName() {
            const drawerName = document.getElementById('drawerName').value.trim();
            if (!drawerName) {
                alert("กรุณากรอกชื่อของคุณก่อนครับ");
                return;
            }

            const response = await fetch('/api/draw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ drawer_name: drawerName })
            });

            const data = await response.json();

            if (response.ok) {
                document.getElementById('draw-section').style.display = 'none';
                document.getElementById('result').innerText = `🎉 คุณจับได้: ${data.drawn_name} 🎉`;
                document.getElementById('shareBtn').style.display = 'inline-block';
            } else {
                alert(data.error);
            }
        }

        function shareLink() {
            const url = window.location.origin;
            navigator.clipboard.writeText(url).then(() => {
                alert("คัดลอกลิงก์แล้ว! ส่งให้เพื่อนต่อได้เลย");
            });
        }
    </script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <style>
        body { font-family: sans-serif; margin: 40px; }
        .box { border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Admin Dashboard 🛡️</h1>
    
    <div class="box">
        <h3>เพิ่มรายชื่อลงในกล่องสุ่ม</h3>
        <input type="text" id="newName" placeholder="พิมพ์ชื่อ...">
        <button onclick="addName()">เพิ่มชื่อ</button>
        <p><strong>รายชื่อในกล่องตอนนี้:</strong> <span id="poolList">{{ pool | join(', ') }}</span></p>
    </div>

    <div class="box">
        <h3>ประวัติการสุ่ม (เห็นได้เฉพาะ Admin)</h3>
        <ul>
            {% for record in history %}
                <li><strong>{{ record.drawer }}</strong> จับได้ <strong>{{ record.drawn }}</strong></li>
            {% endfor %}
        </ul>
    </div>

    <script>
        async function addName() {
            const name = document.getElementById('newName').value.trim();
            if(!name) return;

            const response = await fetch('/api/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });
            
            if(response.ok) {
                location.reload(); // รีเฟรชเพื่อดูรายชื่ออัปเดต
            }
        }
    </script>
</body>
</html>
"""

# ==========================================
# Backend Routes (API)
# ==========================================

@app.route('/')
def index():
    # หน้าเว็บสำหรับคนทั่วไปเข้ามาสุ่ม
    return render_template_string(USER_HTML)

@app.route('/admin')
def admin():
    # ตรวจสอบสิทธิ์ผ่าน URL parameter (เช่น /admin?key=mysecret)
    key = request.args.get('key')
    if key != ADMIN_SECRET:
        return "Unauthorized. คุณไม่มีสิทธิ์เข้าถึงหน้านี้ครับ", 401
    
    return render_template_string(ADMIN_HTML, pool=db['pool'], history=db['history'])

@app.route('/api/add', methods=['POST'])
def add_name():
    name = request.json.get('name')
    if name and name not in db['pool']:
        db['pool'].append(name)
    return jsonify({"success": True, "pool": db['pool']})

@app.route('/api/draw', methods=['POST'])
def draw():
    drawer_name = request.json.get('drawer_name')
    
    if not db['pool']:
        return jsonify({"error": "ไม่มีรายชื่อเหลือในกล่องแล้วครับ!"}), 400
        
    # ป้องกันไม่ให้สุ่มได้ตัวเอง (ถ้ามีชื่อตัวเองอยู่ใน pool)
    valid_choices = [n for n in db['pool'] if n != drawer_name]
    
    if not valid_choices:
        return jsonify({"error": "รายชื่อที่เหลืออยู่มีแค่ชื่อคุณเอง สุ่มไม่ได้ครับ!"}), 400
        
    # สุ่มชื่อ 1 คน
    drawn_name = random.choice(valid_choices)
    
    # เอาชื่อนั้นออกจากกล่อง
    db['pool'].remove(drawn_name)
    
    # บันทึกประวัติ
    db['history'].append({"drawer": drawer_name, "drawn": drawn_name})
    
    return jsonify({"drawn_name": drawn_name})

if __name__ == '__main__':
    # รันเซิร์ฟเวอร์
    app.run(debug=True, port=5000)