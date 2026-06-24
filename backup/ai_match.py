def match_organ(db, organ, blood):
    return db.conn.execute(
        "SELECT username,name FROM users WHERE blood=?",
        (blood,)
    ).fetchall()
