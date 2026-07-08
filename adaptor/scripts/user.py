import hashlib
import sqlite3

from scripts.utils import logger


def hash_password(password: str, salt: str = "dummy") -> str:
    """Hash passwords with sha256"""
    sha256 = hashlib.sha256()
    sha256.update((password.lower().replace(" ", "") + salt).encode())
    return sha256.hexdigest()


def connect_to_db_user():
    """Initialize connection with user list database"""
    try:
        return sqlite3.connect("adaptor/data/user_list.db")
    except Exception as e:
        logger.warning(f"Failed to connect users db: {e}")


def init_db_user() -> None:
    """Create table within database to store users"""
    if conn := connect_to_db_user():
        c = conn.cursor()
        exec_query = """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
        )"""
        c.execute(exec_query)
        conn.commit()
        conn.close()
    else:
        raise


def check_username(username: str):
    """Check if the username is already taken"""
    if conn := connect_to_db_user():
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM users WHERE username = ?",
            (username.lower().replace(" ", ""),),
        )
        row = c.fetchone()[0]
        count = row > 0
        conn.close()
        if count:
            return False
        return True


def signup_user(username: str, password: str) -> None:
    """Store user credentials in the database"""
    if conn := connect_to_db_user():
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username.lower().replace(" ", ""), hash_password(password)),
        )
        conn.commit()
        conn.close()


def singin_user(username: str, password: str):
    """User login process"""
    if conn := connect_to_db_user():
        c = conn.cursor()
        c.execute(
            "SELECT * FROM users WHERE username = ?",
            (username.lower().replace(" ", ""),),
        )
        user_data = c.fetchone()
        conn.close()
        if user_data:
            hashed_password = user_data[-1]
            if hashed_password == hash_password(password):
                return True
            else:
                return False
        else:
            return False
    else:
        return False
