from flask import Flask, request, send_file, jsonify
import pyautogui
from flask_cors import CORS
import socket
import qrcode
import io
import sys
import logging
import os
import signal

# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Allow all origins and methods for testing
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

def get_local_ip():
    try:
        # Get the local IP address by creating a temporary socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_client_ip():
    # Check for proxy headers first
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    # Then check for real IP header
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    # Finally use remote address
    return request.remote_addr

def generate_qr_code():
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create ASCII art for console
    return qr.print_ascii(invert=True), url

@app.route('/network-check', methods=['GET', 'OPTIONS'])
def network_check():
    try:
        client_ip = get_client_ip()
        server_ip = get_local_ip()
        
        logger.info(f"Network check - Client IP: {client_ip}, Server IP: {server_ip}")
        
        # Check if they're on the same subnet
        client_subnet = '.'.join(client_ip.split('.')[:3])
        server_subnet = '.'.join(server_ip.split('.')[:3])
        
        return jsonify({
            'client_ip': client_ip,
            'server_ip': server_ip,
            'same_network': client_subnet == server_subnet,
            'status': 'connected'
        })
    except Exception as e:
        logger.error(f"Network check error: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/qr')
def serve_qr():
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    
    # Generate QR code image
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return send_file(img_bytes, mimetype='image/png')

@app.route('/')
def index():
    return send_file('templates/index.html')

@app.route('/move', methods=['POST'])
def move_mouse():
    data = request.json
    x = data.get('x', 0)
    y = data.get('y', 0)
    relative = data.get('relative', True)
    
    if relative:
        current_x, current_y = pyautogui.position()
        pyautogui.moveRel(x, y)
    else:
        pyautogui.moveTo(x, y)
    
    return jsonify({'status': 'success'})

@app.route('/click', methods=['POST'])
def click_mouse():
    data = request.json
    button = data.get('button', 'left')
    pyautogui.click(button=button)
    return jsonify({'status': 'success'})

@app.route('/type', methods=['POST'])
def type_text():
    data = request.json
    text = data.get('text', '')
    
    # Handle special keys
    if text == '{BACKSPACE}':
        pyautogui.press('backspace')
    elif text == '{ENTER}':
        pyautogui.press('enter')
    else:
        pyautogui.typewrite(text)
    
    return jsonify({'status': 'success'})

@app.route('/kill', methods=['POST'])
def kill_server():
    logger.info("Kill switch activated - shutting down server")
    # Schedule the server shutdown
    def shutdown():
        os.kill(os.getpid(), signal.SIGTERM)
    from threading import Timer
    Timer(1.0, shutdown).start()
    return jsonify({'status': 'shutting_down'})

if __name__ == '__main__':
    ip = get_local_ip()
    qr_ascii, url = generate_qr_code()
    
    print("\n=== Server Starting ===")
    print(f"Server IP: {ip}")
    print(f"URL: http://{ip}:5000")
    print("\nDebug Information:")
    print("1. Check if your phone and computer are on the same network")
    print("2. Make sure no firewall is blocking port 5000")
    print("3. Try accessing the URL in your phone's browser")
    print("\nPress Ctrl+C to stop the server")
    
    # Enable debug mode for better error messages
    app.run(host='0.0.0.0', port=5000, debug=True)
