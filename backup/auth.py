import sqlite3
import hashlib

DB_NAME = "lifelink.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(input_pass, db_pass):
    return input_pass == db_pass or hash_password(input_pass) == db_pass


# ---------------- HOSPITAL LOGIN ----------------
def login_hospital(username, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM hospitals WHERE username=?", (username,))
    hospital = cur.fetchone()

    conn.close()

    if hospital and verify_password(password, hospital[3]):
        return hospital

    return None


# ---------------- USER LOGIN ----------------
def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()

    conn.close()

    if user and verify_password(password, user[1]):
        return user

    return None
