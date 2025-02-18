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
from time import sleep
from modules.cursor_control import CursorController
import threading  # Import the threading module

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

# Initialize cursor controller
cursor = CursorController()

def perform_move(x, y, relative):
    """Helper function to perform mouse movement in a thread."""
    cursor.move_cursor(x, y, relative)

@app.route('/move', methods=['POST'])
def move_mouse():
    data = request.json
    x = data.get('x', 0)
    y = data.get('y', 0)
    relative = data.get('relative', True)

    # Create and start a thread for mouse movement
    move_thread = threading.Thread(target=perform_move, args=(x, y, relative))
    move_thread.start()

    return jsonify({'status': 'success'})

def perform_click(button):
    """Helper function to perform mouse click in a thread."""
    pyautogui.click(button=button)

@app.route('/click', methods=['POST'])
def click_mouse():
    data = request.json
    button = data.get('button', 'left')

    # Create and start a thread for mouse click
    click_thread = threading.Thread(target=perform_click, args=(button,))
    click_thread.start()

    return jsonify({'status': 'success'})

def perform_type(text):
    """Helper function to perform typing in a thread."""
    # Handle special keys
    if text == '{BACKSPACE}':
        pyautogui.press('backspace')
    elif text == '{ENTER}':
        pyautogui.press('enter')
    else:
        pyautogui.typewrite(text)

@app.route('/type', methods=['POST'])
def type_text():
    data = request.json
    text = data.get('text', '')

    # Create and start a thread for typing
    type_thread = threading.Thread(target=perform_type, args=(text,))
    type_thread.start()

    return jsonify({'status': 'success'})

@app.route('/gesture', methods=['POST'])
def handle_gesture():
    data = request.json
    gesture_type = data.get('type')
    
    if gesture_type == 'scroll':
        delta = data.get('deltaY', 0)
        # Make scrolling more responsive
        scroll_amount = int(delta / 5)  # Adjusted sensitivity
        if abs(scroll_amount) > 0:
            pyautogui.scroll(scroll_amount)
    
    elif gesture_type == 'pinch':
        scale = data.get('scale', 1)
        # More responsive zoom thresholds
        if scale > 1.05:  # Reduced threshold for zooming
            pyautogui.hotkey('ctrl', '+')
        elif scale < 0.95:
            pyautogui.hotkey('ctrl', '-')
    
    elif gesture_type == 'three_finger_swipe':
        direction = data.get('direction')
        if direction == 'up':
            pyautogui.hotkey('win', 'tab')
        elif direction == 'down':
            pyautogui.hotkey('win', 'd')
        elif direction == 'left':
            pyautogui.hotkey('alt', 'left')
        elif direction == 'right':
            pyautogui.hotkey('alt', 'right')
    
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

@app.route('/input-focus', methods=['POST'])
def handle_input_focus():
    """Handle input field focus events from the system"""
    data = request.json
    is_focused = data.get('focused', False)
    return jsonify({'status': 'success', 'focused': is_focused})

@app.route('/check-focus', methods=['GET'])
def check_focus():
    """Check if any input field is currently focused"""
    import win32gui
    import win32api
    import win32con
    
    try:
        # Get the focused window
        hwnd = win32gui.GetForegroundWindow()
        # Get the focused control
        focused = win32gui.GetFocus()
        # Get the class name of the focused control
        class_name = win32gui.GetClassName(focused).lower()
        
        # List of common input field class names
        input_classes = ['edit', 'textbox', 'richedit', 'textedit']
        is_input = any(input_class in class_name for input_class in input_classes)
        
        return jsonify({
            'focused': is_input,
            'class': class_name
        })
    except:
        return jsonify({'focused': False, 'class': None})

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