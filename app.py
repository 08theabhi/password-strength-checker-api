import math
import string
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def calculate_entropy(password: str) -> float:
    if not password: return 0.0
    freq = {char: password.count(char) / len(password) for char in set(password)}
    entropy = -sum(p * math.log2(p) for p in freq.values())
    return entropy * len(password)

def check_password_strength(password: str) -> dict:
    if not password:
        return {"status": "Waiting...", "color": "#666", "glow": "rgba(102,102,102,0.1)"}
    
    diversity = sum([any(c.islower() for c in password), any(c.isupper() for c in password),
                     any(c.isdigit() for c in password), any(c in string.punctuation for c in password)])
    score = len(password) + (diversity * 3) + (calculate_entropy(password) / 10)
    
    if score < 15: 
        return {"status": "Weak 🔴", "color": "#ff4d4d", "glow": "rgba(255,77,77,0.2)"}
    if score < 25: 
        return {"status": "Medium 🟡", "color": "#ffd700", "glow": "rgba(255,215,0,0.2)"}
    return {"status": "Strong 🚀", "color": "#00ff7f", "glow": "rgba(0,255,127,0.3)"}

@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Password Strength Checker | NetSpray</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { 
            background: #000; 
            color: white; 
            margin: 0; 
            overflow: hidden; 
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        #aura {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 700px;
            height: 700px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
            filter: blur(100px);
            transition: background 0.8s ease;
            z-index: 1;
        }

        .morph-text {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-block;
        }
        .blur-effect {
            filter: blur(15px);
            opacity: 0;
            transform: translateY(10px);
        }

        #starfield {
            position: fixed;
            inset: 0;
            z-index: 0;
        }

        .glass-card {
            background: rgba(10, 10, 10, 0.75);
            backdrop-filter: blur(30px);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 0 60px rgba(0,0,0,0.9);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .company-gradient {
            background: linear-gradient(to right, #ffffff 0%, #a1a1aa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body>
    <canvas id="starfield"></canvas>
    <div id="aura"></div>

    <div class="relative z-10 flex flex-col items-center justify-center min-h-screen p-6">
        <div class="glass-card p-12 rounded-[3.5rem] w-full max-w-md min-h-[550px] text-center">
            
            <div>
                <h1 class="text-xl font-bold tracking-[0.2em] text-white uppercase drop-shadow-md">
                    Password-Strength-Checker
                </h1>
                <div class="w-12 h-[2px] bg-blue-500 mx-auto mt-4 rounded-full opacity-50"></div>
            </div>

            <div class="flex-grow flex flex-col justify-center py-10">
                <p class="text-[10px] font-bold tracking-[0.3em] text-zinc-500 uppercase mb-4">
                    Analyze Security
                </p>
                <input 
                    type="password" 
                    id="passInput"
                    class="w-full bg-transparent border-b border-zinc-800 p-4 text-white text-center text-3xl focus:outline-none focus:border-blue-500 transition-all placeholder:text-zinc-900"
                    placeholder="••••••••"
                >
                <div class="h-24 flex items-center justify-center mt-6">
                    <span id="statusText" class="morph-text text-3xl font-black tracking-tight text-zinc-700">Waiting...</span>
                </div>
            </div>

            <div class="pt-8 border-t border-white/5">
                <h2 class="company-gradient text-lg font-bold tracking-tight mb-1">
                    NetSpray technologies pvt ltd
                </h2>
                <p class="text-[9px] font-black tracking-[0.5em] text-zinc-500 uppercase">
                    Built By ABHI
                </p>
            </div>

        </div>
    </div>

    <script>
        // --- ANIMATED STARFIELD ---
        const canvas = document.getElementById('starfield');
        const ctx = canvas.getContext('2d');
        let stars = [];

        function initStars() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            stars = [];
            for(let i=0; i<120; i++) {
                stars.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 1.8,
                    speed: Math.random() * 0.12
                });
            }
        }

        function drawStars() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "rgba(255, 255, 255, 0.25)";
            stars.forEach(s => {
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
                ctx.fill();
                s.y -= s.speed;
                if(s.y < 0) s.y = canvas.height;
            });
            requestAnimationFrame(drawStars);
        }

        // --- PASSWORD LOGIC ---
        const input = document.getElementById('passInput');
        const statusText = document.getElementById('statusText');
        const aura = document.getElementById('aura');

        async function handleUpdate() {
            const password = input.value;
            statusText.classList.add('blur-effect');

            const response = await fetch('/check-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });
            const data = await response.json();

            setTimeout(() => {
                statusText.innerText = data.status;
                statusText.style.color = data.color;
                aura.style.background = `radial-gradient(circle, ${data.glow} 0%, transparent 70%)`;
                statusText.classList.remove('blur-effect');
            }, 200);
        }

        window.addEventListener('resize', initStars);
        input.addEventListener('input', handleUpdate);
        initStars();
        drawStars();
    </script>
</body>
</html>
    """)

@app.route("/check-password", methods=["POST"])
def check_password():
    data = request.get_json()
    return jsonify(check_password_strength(data.get("password", "")))

if __name__ == "__main__":
    app.run(debug=True)