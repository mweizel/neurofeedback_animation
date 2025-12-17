import http.server
import socketserver
import socket
import threading
import json
import time
import re

# Params
UDP_IP = "127.0.0.1"
UDP_PORT = 1977
HTTP_PORT = 8080

# Shared State
latest_value = 0.0
lock = threading.Lock()

def udp_listener():
    global latest_value
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print(f"UDP Listener (Thread) started on {UDP_IP}:{UDP_PORT}")
        while True:
            data, _ = sock.recvfrom(1024)
            string = data.decode('utf-8')
            # Parse (r,g,b)
            # We assume nfrun.py sends (0, 0, val) where val is 0-255
            match = re.match(r'\((\d+),(\d+),(\d+)\)', string)
            if match:
                vals = tuple(map(int, match.groups()))
                # Normalize blue channel
                val_norm = vals[2] / 255.0
                with lock:
                    latest_value = val_norm
    except Exception as e:
        print(f"UDP Error: {e}")
    finally:
        sock.close()

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Allow CORS
            self.end_headers()
            
            with lock:
                val = latest_value
            
            response = json.dumps({"value": val}).encode('utf-8')
            self.wfile.write(response)
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        return # Silence logs to keep terminal clean

def run_server():
    # Start UDP in background
    t = threading.Thread(target=udp_listener, daemon=True)
    t.start()
    
    # Start HTTP
    print(f"HTTP Bridge started on port {HTTP_PORT}. Polling endpoint: /data")
    with socketserver.TCPServer(("", HTTP_PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    run_server()
