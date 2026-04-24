import socket
from app import create_app

app = create_app()

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    ip = get_ip_address()
    print(f"Server running on http://{ip}:5000")
    print(f"Make sure to update your Flutter app's baseUrl to: http://{ip}:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
