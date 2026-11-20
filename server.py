
import http.server
import ssl
import json
import hashlib
from pathlib import Path
from datetime import timezone
from urllib.parse import urlsplit

from cryptography import x509
from cryptography.hazmat.primitives import hashes

BASE_DIR = Path(__file__).resolve().parent

PORT = 8443
CERT_FILE = BASE_DIR / "localhost.crt"
KEY_FILE = BASE_DIR / "localhost.key"


class HTTPSHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            directory=str(BASE_DIR),
            **kwargs
        )

    def send_json(self, data):
        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path

        if path == "/api/certificate":
            try:
                cert_bytes = CERT_FILE.read_bytes()

                cert = x509.load_pem_x509_certificate(
                    cert_bytes
                )

                try:
                    san_ext = cert.extensions.get_extension_for_class(
                        x509.SubjectAlternativeName
                    ).value

                    san = [
                        str(name.value)
                        for name in san_ext
                    ]
                except x509.ExtensionNotFound:
                    san = []

                data = {
                    "subject": cert.subject.rfc4514_string(),
                    "issuer": cert.issuer.rfc4514_string(),
                    "serial_number": format(
                        cert.serial_number, "X"
                    ),
                    "not_before": (
                        cert.not_valid_before_utc.isoformat()
                    ),
                    "not_after": (
                        cert.not_valid_after_utc.isoformat()
                    ),
                    "signature_algorithm": (
                        cert.signature_algorithm_oid._name
                        or cert.signature_algorithm_oid.dotted_string
                    ),
                    "san": san,
                    "fingerprint_sha256": (
                        cert.fingerprint(
                            hashes.SHA256()
                        ).hex().upper()
                    )
                }

                self.send_json(data)

            except Exception as error:
                self.send_error(
                    500,
                    "Certificate processing failed"
                )
                print("Certificate error:", error)

            return

        if path == "/api/certificate/download":
            content = CERT_FILE.read_bytes()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/x-x509-ca-cert"
            )
            self.send_header(
                "Content-Disposition",
                'attachment; filename="localhost.crt"'
            )
            self.send_header(
                "Content-Length",
                str(len(content))
            )
            self.end_headers()
            self.wfile.write(content)
            return

        # Only serve the public HTML page.
        # Never expose private keys or CA files.
        if path in ("/", "/index.html"):
            content = (BASE_DIR / "index.html").read_bytes()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(content))
            )
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_error(404, "Not Found")


server = http.server.HTTPServer(
    ("127.0.0.1", PORT),
    HTTPSHandler
)

context = ssl.SSLContext(
    ssl.PROTOCOL_TLS_SERVER
)

context.load_cert_chain(
    certfile=str(CERT_FILE),
    keyfile=str(KEY_FILE)
)

server.socket = context.wrap_socket(
    server.socket,
    server_side=True
)

print("=" * 45)
print("PKI & CHAIN OF TRUST - GROUP N05")
print(f"HTTPS Server: https://localhost:{PORT}")
print("Certificate API: /api/certificate")
print("Press Ctrl+C to stop")
print("=" * 45)

server.serve_forever()
