from flask import Flask, request, jsonify, render_template_string
import random
import os
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"  # รหัสผ่านเข้าหน้า Admin

# --- DATA STORAGE (In-Memory) ---
# ล้างรายชื่อเริ่มต้นออกทั้งหมดตามที่แจ้งครับ (ให้ Admin ใส่เองผ่านหน้าเว็บ)
db = {
    "all_names": [],
    "remaining_pool": [],
    "exclusions": [],
    "history": []
}

# --- UI TEMPLATE (Indigo Theme) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Secret Box - นครนายก 2026</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #020617; color: #f8fafc; }
        .glass-card { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .btn-indigo { background: #4f46e5; transition: all 0.2s; }
        .btn-indigo:hover { background: #4338ca; transform: translateY(-1px); }
        .btn-indigo:active { transform: translateY(0); scale: 0.98; }
        .custom-shadow { box-shadow: 0 0 50px -12px rgba(79, 70, 229, 0.3); }
        select { 
            appearance: none; 
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236366f1'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E"); 
            background-repeat: no-repeat; 
            background-position: right 1rem center; 
            background-size: 1.5em; 
        }
    </style>
</head>
<body class="min-h-screen p-4 flex flex-col items-center justify-center">
    <div class="max-w-md w-full space-y-8 py-10">
        
        <!-- View Switcher -->
        <div id="nav-tabs" class="flex justify-center mb-6">
            <div class="bg-slate-900/80 p-1.5 rounded-2xl border border-white/5 flex shadow-2xl">
                <button onclick="switchView('user')" id="tab-user" class="flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all bg-indigo-600 text-white shadow-lg">
                    <i data-lucide="gift" class="w-4 h-4"></i>
                    <span>สุ่มชื่อ</span>
                </button>
                <button onclick="showAdminLogin()" id="tab-admin" class="flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all text-slate-500 hover:text-slate-300">
                    <i data-lucide="shield" class="w-4 h-4"></i>
                    <span>แอดมิน</span>
                </button>
            </div>
        </div>

        <!-- User View -->
        <div id="user-view" class="space-y-6 animate-in fade-in duration-700">
            <div id="main-card" class="glass-card rounded-[2.5rem] p-10 shadow-2xl custom-shadow border border-white/5 relative overflow-hidden">
                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-30"></div>
                
                <div id="draw-initial" class="space-y-8 text-center">
                    <div class="space-y-4">
                        <div class="w-20 h-20 bg-indigo-600/10 rounded-3xl flex items-center justify-center mx-auto border border-indigo-500/20 shadow-inner">
                            <i data-lucide="play" class="text-indigo-400 fill-indigo-400 ml-1 w-10 h-10"></i>
                        </div>
                        <h2 class="text-3xl font-black tracking-tight italic">The Secret Box</h2>
                        <p class="text-slate-500 text-xs font-medium uppercase tracking-[0.2em]">เลือกชื่อของคุณเพื่อเริ่มสุ่ม</p>
                    </div>

                    <div class="space-y-6 text-left">
                        <div class="space-y-3">
                            <label class="text-[10px] font-black text-indigo-400 uppercase tracking-widest ml-1">มึงคือใคร?</label>
                            <select id="drawer-select" class="w-full bg-slate-950 border border-slate-800 rounded-2xl px-6 py-5 text-center text-xl font-bold text-white shadow-inner focus:outline-none focus:border-indigo-500 transition-all cursor-pointer">
                                <option value="">กำลังโหลดรายชื่อ...</option>
                            </select>
                        </div>
                        <button onclick="performDraw()" id="draw-btn" class="w-full py-5 rounded-2xl font-black text-xl btn-indigo text-white shadow-xl shadow-indigo-950/50">
                            🎲 สุ่มเลย!
                        </button>
                    </div>

                    <div class="pt-2">
                        <div class="inline-flex items-center space-x-2 px-4 py-1.5 bg-slate-950/50 rounded-full text-[10px] font-bold text-slate-500 border border-slate-800/50">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span id="pool-count">คงเหลือในกล่อง: -- ชื่อ</span>
                        </div>
                    </div>
                </div>

                <div id="draw-result" class="hidden text-center space-y-10 py-6 animate-in zoom-in duration-500">
                    <div class="relative">
                        <div class="absolute inset-0 bg-indigo-500/10 blur-3xl rounded-full scale-150"></div>
                        <div class="relative">
                            <p class="text-slate-400 mb-6 font-black uppercase tracking-[0.2em] text-[10px]">คุณสุ่มได้...</p>
                            <h2 id="result-name" class="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-indigo-300 via-emerald-300 to-indigo-300 tracking-tighter drop-shadow-2xl py-2">---</h2>
                        </div>
                    </div>
                    <div class="p-6 bg-emerald-500/5 border border-emerald-500/10 rounded-3xl">
                        <p class="text-emerald-300/80 text-sm font-medium leading-relaxed">
                            แคปหน้าจอเก็บไว้เลย<br/>
                            <span class="text-emerald-400 font-black">ความลับนะ ห้ามบอกใคร!</span>
                        </p>
                    </div>
                    <button onclick="location.reload()" class="text-slate-600 text-[10px] font-black uppercase tracking-[0.2em] hover:text-slate-400 transition-colors">กลับหน้าแรก</button>
                </div>
            </div>
        </div>

        <!-- Admin View -->
        <div id="admin-view" class="hidden space-y-6 animate-in slide-in-from-bottom-4 duration-500">
            <div class="flex justify-between items-center px-4">
                <h2 class="text-xl font-black flex items-center space-x-2">
                    <span class="bg-indigo-600 w-2 h-6 rounded-full inline-block"></span>
                    <span>Admin Panel</span>
                </h2>
                <button onclick="location.reload()" class="bg-slate-900 p-2.5 rounded-xl border border-white/5 text-slate-500 hover:text-white transition-colors">
                    <i data-lucide="log-out" class="w-5 h-5"></i>
                </button>
            </div>

            <section class="bg-slate-900 p-8 rounded-[2rem] border border-white/5 shadow-xl space-y-6">
                <div class="flex items-center space-x-2 font-black text-indigo-400 mb-2">
                    <i data-lucide="user-plus" class="w-4 h-4"></i>
                    <span class="uppercase tracking-widest text-xs">จัดการรายชื่อ</span>
                </div>
                <div class="space-y-3">
                    <textarea id="bulk-names" rows="3" placeholder="ใส่ชื่อเพื่อน (1 ชื่อต่อ 1 บรรทัด)..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-4 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none shadow-inner"></textarea>
                    <button onclick="addNames()" class="w-full bg-indigo-600 py-3 rounded-xl text-xs font-black text-white hover:bg-indigo-500 transition-all">บันทึกรายชื่อ</button>
                </div>
                <div id="admin-names-list" class="flex flex-wrap gap-2 max-h-48 overflow-y-auto pr-1"></div>
            </section>

            <section class="bg-slate-900 p-8 rounded-[2rem] border border-white/5 shadow-xl space-y-6">
                <h3 class="flex items-center space-x-2 font-black text-rose-400">
                    <i data-lucide="heart-off" class="w-4 h-4"></i>
                    <span class="uppercase tracking-widest text-xs">คู่ห้าม (ห้ามสุ่มเจอกัน)</span>
                </h3>
                <div class="grid grid-cols-2 gap-3">
                    <select id="ex-1" class="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-bold text-white outline-none"></select>
                    <select id="ex-2" class="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-bold text-white outline-none"></select>
                </div>
                <button onclick="addExclusion()" class="w-full bg-rose-600/10 hover:bg-rose-600/20 text-rose-400 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest border border-rose-500/20">ห้ามสุ่มเจอกัน</button>
                <div id="admin-ex-list" class="space-y-2 mt-4"></div>
            </section>

            <section class="bg-slate-900 p-8 rounded-[2.5rem] border border-white/5 shadow-xl">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="flex items-center space-x-2 font-black text-emerald-400">
                        <i data-lucide="history" class="w-4 h-4"></i>
                        <span class="uppercase tracking-widest text-xs">ประวัติ (ความลับแอดมิน)</span>
                    </h3>
                    <button onclick="resetData()" class="text-[9px] font-black text-rose-500 border border-rose-500/30 px-2 py-1 rounded-md">RESET ALL</button>
                </div>
                <div id="admin-history-list" class="space-y-3"></div>
            </section>
        </div>
    </div>

    <!-- Login Modal -->
    <div id="login-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 hidden">
        <div class="absolute inset-0 bg-black/90 backdrop-blur-sm" onclick="closeAdminLogin()"></div>
        <div class="glass-card w-full max-w-xs p-8 rounded-[2.5rem] border border-indigo-500/30 relative z-10 shadow-2xl">
            <div class="text-center space-y-6">
                <div class="w-16 h-16 bg-indigo-500/10 rounded-2xl flex items-center justify-center mx-auto border border-indigo-500/20">
                    <i data-lucide="shield" class="text-indigo-500 w-8 h-8"></i>
                </div>
                <h4 class="font-black text-white text-lg tracking-tight">รหัสผ่านแอดมิน</h4>
                <input type="password" id="admin-pw-input" placeholder="••••" class="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-4 text-center text-2xl text-white outline-none focus:border-indigo-500 shadow-inner">
                <button onclick="verifyAdmin()" class="w-full py-4 btn-indigo rounded-xl text-xs font-black text-white">ยืนยัน</button>
            </div>
        </div>
    </div>

    <script>
        async function fetchState() {
            const res = await fetch('/api/state');
            const data = await res.json();
            renderUI(data);
        }

        function renderUI(data) {
            const select = document.getElementById('drawer-select');
            const historyDrawers = data.history.map(h => h.drawer);
            const availableToDraw = data.all_names.filter(name => !historyDrawers.includes(name));

            if (data.all_names.length === 0) {
                select.innerHTML = '<option value="">(แอดมินยังไม่เพิ่มรายชื่อ)</option>';
            } else {
                let optionsHtml = '<option value="" selected disabled>-- เลือกชื่อตัวเอง --</option>';
                optionsHtml += availableToDraw.map(n => `<option value="${n}">${n}</option>`).join('');
                if (historyDrawers.length > 0) {
                    optionsHtml += '<optgroup label="สุ่มไปแล้ว ✅">';
                    optionsHtml += historyDrawers.map(n => `<option disabled>${n} (เรียบร้อย)</option>`).join('');
                    optionsHtml += '</optgroup>';
                }
                select.innerHTML = optionsHtml;
            }

            document.getElementById('pool-count').innerText = `คงเหลือในกล่อง: ${data.remaining_pool.length} ชื่อ`;

            document.getElementById('admin-names-list').innerHTML = data.all_names.map(name => 
                `<span class="bg-slate-800 border border-white/5 px-3 py-1.5 rounded-xl text-[11px] font-bold flex items-center space-x-2 animate-in zoom-in">
                    <span>${name}</span>
                    <button onclick="removeName('${name}')" class="text-rose-500 hover:text-rose-400">
                        <i data-lucide="x" class="w-3 h-3"></i>
                    </button>
                </span>`
            ).join('');

            document.getElementById('admin-ex-list').innerHTML = data.exclusions.map((ex, idx) => 
                `<div class="flex justify-between items-center bg-rose-500/5 p-3 rounded-xl border border-rose-500/10 text-[11px]">
                    <span class="text-rose-300 font-bold">${ex.p1} <span class="mx-2 opacity-30">❌</span> ${ex.p2}</span>
                    <button onclick="removeExclusion(${idx})"><i data-lucide="trash-2" class="w-3 h-3 text-rose-500"></i></button>
                </div>`
            ).join('');

            document.getElementById('admin-history-list').innerHTML = data.history.slice().reverse().map(h => 
                `<div class="bg-slate-950/50 p-4 rounded-xl border border-white/5 flex justify-between items-center text-[11px]">
                    <span><b class="text-indigo-400 font-black">${h.drawer}</b> <span class="mx-2 opacity-30 italic">จับได้</span> <b class="text-emerald-400 font-black">${h.drawn}</b></span>
                    <span class="text-[9px] text-slate-700 font-mono">${h.time}</span>
                </div>`
            ).join('');

            ['ex-1', 'ex-2'].forEach(id => {
                const el = document.getElementById(id);
                el.innerHTML = '<option value="">เลือกชื่อ...</option>' + 
                    data.all_names.map(n => `<option value="${n}">${n}</option>`).join('');
            });

            lucide.createIcons();
        }

        async function performDraw() {
            const drawer = document.getElementById('drawer-select').value;
            if (!drawer) { alert("กรุณาเลือกชื่อตัวเองก่อน!"); return; }

            const btn = document.getElementById('draw-btn');
            btn.disabled = true;
            btn.innerHTML = '<span class="animate-pulse">กำลังสุ่ม...</span>';

            const res = await fetch('/api/draw', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ drawer })
            });
            const result = await res.json();

            if (result.error) {
                alert(result.error);
                location.reload();
                return;
            }

            setTimeout(() => {
                document.getElementById('draw-initial').classList.add('hidden');
                document.getElementById('draw-result').classList.remove('hidden');
                document.getElementById('result-name').innerText = result.drawn;
                lucide.createIcons();
            }, 1000);
        }

        function showAdminLogin() { document.getElementById('login-modal').classList.remove('hidden'); }
        function closeAdminLogin() { document.getElementById('login-modal').classList.add('hidden'); }
        
        function verifyAdmin() {
            const pw = document.getElementById('admin-pw-input').value;
            if (pw === "{{ admin_password }}") {
                switchView('admin');
                closeAdminLogin();
            } else { alert("รหัสผ่านไม่ถูกต้อง"); }
        }

        function switchView(view) {
            document.getElementById('user-view').classList.toggle('hidden', view !== 'user');
            document.getElementById('admin-view').classList.toggle('hidden', view !== 'admin');
            const tabUser = document.getElementById('tab-user');
            const tabAdmin = document.getElementById('tab-admin');
            if (view === 'user') {
                tabUser.className = "flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all bg-indigo-600 text-white shadow-lg";
                tabAdmin.className = "flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all text-slate-500 hover:text-slate-300";
            } else {
                tabAdmin.className = "flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all bg-indigo-600 text-white shadow-lg";
                tabUser.className = "flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all text-slate-500 hover:text-slate-300";
                fetchState();
            }
        }

        async function adminAction(action, body = {}) {
            await fetch(`/api/admin/${action}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            fetchState();
        }

        function addNames() {
            const input = document.getElementById('bulk-names').value;
            const names = input.split('\\n').map(n => n.trim()).filter(n => n);
            if (names.length > 0) {
                adminAction('add_names', { names });
                document.getElementById('bulk-names').value = '';
            }
        }

        function removeName(name) { if (confirm(`ลบชื่อ "${name}"? ประวัติจะถูกลบด้วย`)) adminAction('remove_name', { name }); }
        function addExclusion() {
            const p1 = document.getElementById('ex-1').value;
            const p2 = document.getElementById('ex-2').value;
            if (p1 && p2 && p1 !== p2) adminAction('add_exclusion', { p1, p2 });
        }
        function removeExclusion(index) { adminAction('remove_exclusion', { index }); }
        function resetData() { if (confirm("ล้างข้อมูลทั้งหมด?")) adminAction('reset'); }

        fetchState();
        lucide.createIcons();
    </script>
</body>
</html>
"""

# --- API ROUTES ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, admin_password=ADMIN_PASSWORD)

@app.route('/api/state')
def get_state():
    return jsonify(db)

@app.route('/api/draw', methods=['POST'])
def draw_name():
    data = request.json
    drawer = data.get('drawer')
    
    if any(h['drawer'] == drawer for h in db['history']):
        return jsonify({"error": "คุณสุ่มไปแล้ว!"}), 400

    forbidden = []
    for ex in db['exclusions']:
        if ex['p1'] == drawer: forbidden.append(ex['p2'])
        if ex['p2'] == drawer: forbidden.append(ex['p1'])

    options = [n for n in db['remaining_pool'] if n != drawer and n not in forbidden]
    
    if not options:
        return jsonify({"error": "ไม่เหลือชื่อที่สุ่มได้ตามเงื่อนไข"}), 400

    result = random.choice(options)
    db['remaining_pool'].remove(result)
    db['history'].append({
        "drawer": drawer,
        "drawn": result,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    return jsonify({"drawn": result})

@app.route('/api/admin/<action>', methods=['POST'])
def admin_api(action):
    data = request.json
    if action == 'add_names':
        for n in data['names']:
            if n not in db['all_names']:
                db['all_names'].append(n)
                db['remaining_pool'].append(n)
    elif action == 'remove_name':
        name = data['name']
        db['all_names'] = [n for n in db['all_names'] if n != name]
        db['remaining_pool'] = [n for n in db['remaining_pool'] if n != name]
        db['history'] = [h for h in db['history'] if h['drawer'] != name and h['drawn'] != name]
    elif action == 'add_exclusion':
        db['exclusions'].append({"p1": data['p1'], "p2": data['p2']})
    elif action == 'remove_exclusion':
        db['exclusions'].pop(data['index'])
    elif action == 'reset':
        db['all_names'], db['remaining_pool'], db['history'], db['exclusions'] = [], [], [], []
    
    return jsonify({"success": True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)