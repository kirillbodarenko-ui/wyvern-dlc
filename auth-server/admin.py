import argparse
import base64
import getpass
import os
import secrets
import sqlite3
import sys
import time
from pathlib import Path

from server import PBKDF2_ITERATIONS, password_hash


DB_PATH = Path(os.getenv("AUTH_DB", "/data/licenses.db"))


def connection() -> sqlite3.Connection:
    value = sqlite3.connect(DB_PATH)
    value.row_factory = sqlite3.Row
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Управление лицензиями Karitsa")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-user")
    create.add_argument("username")
    create.add_argument("--password-stdin", action="store_true")
    reset = commands.add_parser("reset-hwid")
    reset.add_argument("username")
    for name in ("enable", "disable", "delete"):
        command = commands.add_parser(name)
        command.add_argument("username")
    commands.add_parser("list")
    args = parser.parse_args()

    with connection() as db:
        if args.command == "create-user":
            password = sys.stdin.readline().rstrip("\r\n") if args.password_stdin else getpass.getpass(
                "Новый пароль (минимум 8 символов): ")
            if len(password) < 8:
                raise SystemExit("Пароль слишком короткий")
            salt = secrets.token_bytes(16)
            digest = password_hash(password, salt)
            db.execute(
                "INSERT INTO users(username,password_salt,password_hash,created_at) VALUES(?,?,?,?)",
                (args.username, base64.b64encode(salt).decode(), base64.b64encode(digest).decode(), int(time.time())),
            )
            print(f"Аккаунт {args.username} создан")
        elif args.command == "reset-hwid":
            result = db.execute("UPDATE users SET hwid_hash = NULL WHERE username = ?", (args.username,))
            print("HWID сброшен" if result.rowcount else "Аккаунт не найден")
        elif args.command in ("enable", "disable"):
            enabled = 1 if args.command == "enable" else 0
            result = db.execute("UPDATE users SET enabled = ? WHERE username = ?", (enabled, args.username))
            print("Готово" if result.rowcount else "Аккаунт не найден")
        elif args.command == "delete":
            result = db.execute("DELETE FROM users WHERE username = ?", (args.username,))
            print("Аккаунт удалён" if result.rowcount else "Аккаунт не найден")
        else:
            rows = db.execute("SELECT username, enabled, hwid_hash, created_at, last_login_at FROM users ORDER BY username").fetchall()
            for row in rows:
                print(f"{row['username']}: enabled={bool(row['enabled'])}, hwid={'yes' if row['hwid_hash'] else 'no'}, last={row['last_login_at']}")


if __name__ == "__main__":
    main()
