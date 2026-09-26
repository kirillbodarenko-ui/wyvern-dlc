import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DB_PATH = Path(os.getenv("AUTH_DB", "/data/licenses.db"))
BOOTSTRAP_FILE = Path(os.getenv("AUTH_BOOTSTRAP_FILE", "/app/bootstrap-users.json"))
TOKEN_SECRET = os.getenv("AUTH_TOKEN_SECRET", "")
SUPPORT_URL = os.getenv("AUTH_SUPPORT_URL", "https://funpay.com/users/21337436/")
CLIENT_VERSION = os.getenv("AUTH_CLIENT_VERSION", "0.1-recode")
TOKEN_TTL_SECONDS = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "300"))
PBKDF2_ITERATIONS = 310_000

if len(TOKEN_SECRET) < 32:
    raise RuntimeError("AUTH_TOKEN_SECRET must contain at least 32 characters")

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
rate_lock = threading.Lock()
attempts: dict[str, deque[float]] = defaultdict(deque)


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                hwid_hash TEXT,
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at INTEGER NOT NULL,
                last_login_at INTEGER
            )
        """)


def import_bootstrap_users() -> None:
    if not BOOTSTRAP_FILE.is_file():
        return
    users = json.loads(BOOTSTRAP_FILE.read_text(encoding="utf-8"))
    if not isinstance(users, list):
        raise RuntimeError("AUTH_BOOTSTRAP_FILE must contain a JSON array")
    with db() as connection:
        for user in users:
            username = str(user["username"]).strip()
            salt = str(user["passwordSalt"])
            digest = str(user["passwordHash"])
            if not (3 <= len(username) <= 32):
                raise RuntimeError("Invalid bootstrap username")
            if len(base64.b64decode(salt)) != 16 or len(base64.b64decode(digest)) != 32:
                raise RuntimeError("Invalid bootstrap password hash")
            connection.execute(
                """INSERT OR IGNORE INTO users
                   (username, password_salt, password_hash, created_at)
                   VALUES (?, ?, ?, ?)""",
                (username, salt, digest, int(time.time())),
            )


def password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, 32)


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def issue_token(username: str, hwid_hash: str) -> tuple[str, int]:
    expires_at = int(time.time()) + TOKEN_TTL_SECONDS
    payload = b64url(json.dumps({
        "sub": username,
        "hwid": hwid_hash,
        "exp": expires_at,
        "nonce": secrets.token_hex(12),
    }, separators=(",", ":")).encode("utf-8"))
    signature = b64url(hmac.new(TOKEN_SECRET.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).digest())
    return f"{payload}.{signature}", expires_at


def verify_token(token: str, hwid_hash: str) -> str | None:
    try:
        payload_part, signature_part = token.split(".", 1)
        expected = hmac.new(TOKEN_SECRET.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, b64url_decode(signature_part)):
            return None
        payload = json.loads(b64url_decode(payload_part))
        if int(payload["exp"]) < int(time.time()) or not hmac.compare_digest(payload["hwid"], hwid_hash):
            return None
        username = str(payload["sub"])
        with db() as connection:
            row = connection.execute(
                "SELECT enabled, hwid_hash FROM users WHERE username = ?", (username,)
            ).fetchone()
        if row is None or not row["enabled"] or row["hwid_hash"] != hwid_hash:
            return None
        return username
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def rate_limited(address: str) -> bool:
    now = time.monotonic()
    with rate_lock:
        bucket = attempts[address]
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= 10:
            return True
        bucket.append(now)
        return False


class AuthHandler(BaseHTTPRequestHandler):
    server_version = "KaritsaAuth/1.0"

    def log_message(self, message: str, *args) -> None:
        print(f"{self.address_string()} - {message % args}")

    def send_json(self, status: int, body: dict) -> None:
        encoded = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def read_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 8192:
                return None
            value = json.loads(self.rfile.read(length))
            return value if isinstance(value, dict) else None
        except (ValueError, json.JSONDecodeError):
            return None

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json(200, {"ok": True})
        else:
            self.send_json(404, {"ok": False, "code": "not_found"})

    def do_POST(self) -> None:
        if self.path == "/api/v1/login":
            self.handle_login()
        elif self.path == "/api/v1/validate":
            self.handle_validate()
        else:
            self.send_json(404, {"ok": False, "code": "not_found"})

    def handle_login(self) -> None:
        if rate_limited(self.client_address[0]):
            self.send_json(429, {"ok": False, "code": "rate_limited", "message": "Слишком много попыток"})
            return
        body = self.read_json()
        if body is None:
            self.send_json(400, {"ok": False, "code": "invalid_request"})
            return
        username = str(body.get("username", "")).strip()
        password = str(body.get("password", ""))
        hwid_hash = str(body.get("hwid", ""))
        version = str(body.get("version", ""))
        if not (3 <= len(username) <= 32 and 8 <= len(password) <= 256 and len(hwid_hash) == 64):
            self.send_json(400, {"ok": False, "code": "invalid_request"})
            return
        if version != CLIENT_VERSION:
            self.send_json(426, {"ok": False, "code": "update_required", "message": "Версия клиента не поддерживается"})
            return

        connection = db()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if row is None:
                connection.rollback()
                self.send_json(401, {"ok": False, "code": "bad_credentials", "message": "Неверный логин или пароль"})
                return
            salt = base64.b64decode(row["password_salt"])
            actual_hash = password_hash(password, salt)
            if not hmac.compare_digest(actual_hash, base64.b64decode(row["password_hash"])):
                connection.rollback()
                self.send_json(401, {"ok": False, "code": "bad_credentials", "message": "Неверный логин или пароль"})
                return
            if not row["enabled"]:
                connection.rollback()
                self.send_json(403, {"ok": False, "code": "disabled", "message": "Лицензия заблокирована"})
                return
            if row["hwid_hash"] is None:
                connection.execute(
                    "UPDATE users SET hwid_hash = ?, last_login_at = ? WHERE id = ?",
                    (hwid_hash, int(time.time()), row["id"]),
                )
            elif not hmac.compare_digest(row["hwid_hash"], hwid_hash):
                connection.rollback()
                self.send_json(409, {
                    "ok": False,
                    "code": "hwid_mismatch",
                    "message": "Аккаунт привязан к другому компьютеру",
                    "supportUrl": SUPPORT_URL,
                })
                return
            else:
                connection.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (int(time.time()), row["id"]))
            connection.commit()
            token, expires_at = issue_token(row["username"], hwid_hash)
            self.send_json(200, {"ok": True, "token": token, "expiresAt": expires_at})
        finally:
            connection.close()

    def handle_validate(self) -> None:
        body = self.read_json()
        auth = self.headers.get("Authorization", "")
        if body is None or not auth.startswith("Bearer "):
            self.send_json(401, {"ok": False, "code": "invalid_session"})
            return
        hwid_hash = str(body.get("hwid", ""))
        username = verify_token(auth[7:], hwid_hash)
        if username is None:
            self.send_json(401, {"ok": False, "code": "invalid_session"})
            return
        token, expires_at = issue_token(username, hwid_hash)
        self.send_json(200, {"ok": True, "token": token, "expiresAt": expires_at})


if __name__ == "__main__":
    initialize_database()
    import_bootstrap_users()
    address = os.getenv("AUTH_BIND", "127.0.0.1")
    port = int(os.getenv("AUTH_PORT", "8787"))
    print(f"Karitsa auth server listening on {address}:{port}")
    ThreadingHTTPServer((address, port), AuthHandler).serve_forever()
