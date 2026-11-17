import os
import socket
from app import create_app, db

app = create_app()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')

    print("=" * 65)
    print(" 👑 NEW LUCKY (SWEETS & DAIRY • FAMILY RESTAURANT • RESIDENCY)")
    print("=" * 65)
    print(f" ▪ Local PC URL:       http://127.0.0.1:{port}")
    print(f" ▪ Mobile / Tablet IP:  http://{local_ip}:{port}")
    print(f" ▪ POS Counter Billing: http://127.0.0.1:{port}/pos")
    print(f" ▪ Hotel Front Desk:    http://127.0.0.1:{port}/hotel-desk")
    print(f" ▪ Dairy Khata Ledger:  http://127.0.0.1:{port}/khata")
    print(f" ▪ Owner Dashboard:     http://127.0.0.1:{port}/admin/dashboard")
    print("=" * 65)

    app.run(host='0.0.0.0', port=port, debug=debug_mode)
