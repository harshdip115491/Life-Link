import sqlite3
import os
import hashlib


class DB:

    def __init__(self):

        os.makedirs("user_images", exist_ok=True)
        os.makedirs("certificates", exist_ok=True)

        self.conn = sqlite3.connect(
            "lifelink.db",
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self.create_tables()
        self.insert_hospitals()
        self.upgrade_database()

    # =========================================
    # PASSWORD HASH
    # =========================================

    def hash_password(self, password):
        return hashlib.sha256(
            password.encode()
        ).hexdigest()

    # =========================================
    # CREATE TABLES
    # =========================================

    def create_tables(self):

        c = self.conn.cursor()

        # =====================================
        # USERS
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (

            username TEXT PRIMARY KEY,
            password TEXT,

            name TEXT,
            dob TEXT,
            gender TEXT,

            blood TEXT,

            aadhaar TEXT UNIQUE,
            phone TEXT UNIQUE,

            family TEXT,
            email TEXT,

            state TEXT,
            district TEXT,
            subdistrict TEXT,

            pincode TEXT,
            address TEXT,

            image TEXT
        )
        """)

        # =====================================
        # HOSPITALS
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE,
            username TEXT UNIQUE,

            password TEXT,

            district TEXT,

            lat REAL,
            lon REAL
        )
        """)

        # =====================================
        # USER REQUESTS
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT,
            name TEXT,

            organ TEXT,
            hospital TEXT,

            priority TEXT,
            note TEXT,

            status TEXT DEFAULT 'Pending',

            datetime TEXT,

            urgency_level TEXT DEFAULT 'Medium',

            waiting_days INTEGER DEFAULT 30,

            age INTEGER DEFAULT 40,

            distance_km REAL DEFAULT 50,

            hospital_success_rate REAL DEFAULT 75,

            icu_available INTEGER DEFAULT 1,

            disease_severity INTEGER DEFAULT 3,

            ai_priority_score REAL DEFAULT 0
        )
        """)

        # =====================================
        # DONATIONS
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS donations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT,
            name TEXT,

            organ TEXT,
            date TEXT
        )
        """)

        # =====================================
        # BANK REQUESTS
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS bank_requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT,
            name TEXT,

            organ TEXT,

            source TEXT,

            status TEXT,

            datetime TEXT,

            emergency_cases INTEGER DEFAULT 1,

            icu_available INTEGER DEFAULT 1,

            success_rate REAL DEFAULT 75,

            distance_km REAL DEFAULT 50,

            surgeon_available INTEGER DEFAULT 1,

            ai_priority_score REAL DEFAULT 0
        )
        """)

        # =====================================
        # INVENTORY
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            organ TEXT,
            quantity INTEGER,

            type TEXT,

            source TEXT,
            destination TEXT,

            datetime TEXT
        )
        """)

        # =====================================
        # EMERGENCY
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS emergency (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT,
            name TEXT,

            place TEXT,
            reason TEXT,

            datetime TEXT,

            status TEXT DEFAULT 'Pending'
        )
        """)

        # =====================================
        # HOSPITAL ALERTS
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS hospital_alerts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            hospital TEXT,

            username TEXT,
            name TEXT,

            datetime TEXT,

            status TEXT DEFAULT 'Pending'
        )
        """)

        # =====================================
        # RECYCLE BIN
        # =====================================

        c.execute("""
        CREATE TABLE IF NOT EXISTS recycle_bin (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            type TEXT,
            data TEXT,

            deleted_at TEXT
        )
        """)

        self.conn.commit()

    # =========================================
    # DATABASE UPGRADE
    # =========================================

    def upgrade_database(self):

        c = self.conn.cursor()

        # =====================================
        # SAFE COLUMN ADDER
        # =====================================

        def add_column_if_not_exists(
            table,
            column,
            definition
        ):

            try:

                columns = c.execute(
                    f"PRAGMA table_info({table})"
                ).fetchall()

                column_names = [
                    col[1]
                    for col in columns
                ]

                if column not in column_names:

                    c.execute(
                        f"""
                        ALTER TABLE {table}
                        ADD COLUMN {column} {definition}
                        """
                    )

            except:
                pass

        # =====================================
        # REQUESTS AI COLUMNS
        # =====================================

        add_column_if_not_exists(
            "requests",
            "urgency_level",
            "TEXT DEFAULT 'Medium'"
        )

        add_column_if_not_exists(
            "requests",
            "waiting_days",
            "INTEGER DEFAULT 30"
        )

        add_column_if_not_exists(
            "requests",
            "age",
            "INTEGER DEFAULT 40"
        )

        add_column_if_not_exists(
            "requests",
            "distance_km",
            "REAL DEFAULT 50"
        )

        add_column_if_not_exists(
            "requests",
            "hospital_success_rate",
            "REAL DEFAULT 75"
        )

        add_column_if_not_exists(
            "requests",
            "icu_available",
            "INTEGER DEFAULT 1"
        )

        add_column_if_not_exists(
            "requests",
            "disease_severity",
            "INTEGER DEFAULT 3"
        )

        add_column_if_not_exists(
            "requests",
            "ai_priority_score",
            "REAL DEFAULT 0"
        )

        # =====================================
        # BANK AI COLUMNS
        # =====================================

        add_column_if_not_exists(
            "bank_requests",
            "emergency_cases",
            "INTEGER DEFAULT 1"
        )

        add_column_if_not_exists(
            "bank_requests",
            "icu_available",
            "INTEGER DEFAULT 1"
        )

        add_column_if_not_exists(
            "bank_requests",
            "success_rate",
            "REAL DEFAULT 75"
        )

        add_column_if_not_exists(
            "bank_requests",
            "distance_km",
            "REAL DEFAULT 50"
        )

        add_column_if_not_exists(
            "bank_requests",
            "surgeon_available",
            "INTEGER DEFAULT 1"
        )

        add_column_if_not_exists(
            "bank_requests",
            "ai_priority_score",
            "REAL DEFAULT 0"
        )

        self.conn.commit()

    # =========================================
    # INSERT DEFAULT HOSPITALS
    # =========================================

    def insert_hospitals(self):

        c = self.conn.cursor()

        hospitals = [

            ("AIIMS Delhi","aiims","123","Delhi",28.5672,77.2100),

            ("Apollo Hospital","apollo","123","Mumbai",19.0760,72.8777),

            ("Fortis Hospital","fortis","123","Delhi",28.7041,77.1025),

            ("Kokilaben Hospital","kokilaben","123","Mumbai",19.1364,72.8256),

            ("Lilavati Hospital","lilavati","123","Mumbai",19.0509,72.8295),

            ("Tata Memorial","tata","123","Mumbai",19.0048,72.8422),

            ("Manipal Hospital","manipal","123","Bangalore",12.9716,77.5946),

            ("Max Hospital","max","123","Delhi",28.6139,77.2090),

            ("Narayana Health","narayana","123","Bangalore",12.9279,77.6271),

            ("Care Hospital","care","123","Hyderabad",17.3850,78.4867),

            ("Ruby Hall","ruby","123","Pune",18.5204,73.8567),

            ("Sahyadri Hospital","sahyadri","123","Pune",18.5314,73.8446),

            ("Wockhardt Hospital","wockhardt","123","Mumbai",19.0176,72.8562),

            ("Global Hospital","global","123","Chennai",13.0827,80.2707),

            ("Medanta","medanta","123","Gurgaon",28.4595,77.0266),

            ("Columbia Asia","columbia","123","Bangalore",12.9352,77.6245),

            ("Hinduja Hospital","hinduja","123","Mumbai",19.0330,72.8406),

            ("Jaslok Hospital","jaslok","123","Mumbai",18.9712,72.8090),

            ("Yashoda Hospital","yashoda","123","Hyderabad",17.4425,78.3913),

            ("Sunshine Hospital","sunshine","123","Hyderabad",17.4399,78.4983)
        ]

        for h in hospitals:

            try:

                hashed_pass = self.hash_password(h[2])

                c.execute("""
                INSERT INTO hospitals
                (name,username,password,district,lat,lon)
                VALUES (?,?,?,?,?,?)
                """, (
                    h[0],
                    h[1],
                    hashed_pass,
                    h[3],
                    h[4],
                    h[5]
                ))

            except:
                pass

        self.conn.commit()
