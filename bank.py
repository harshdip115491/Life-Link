import streamlit as st
from db import DB
from hospital_ai import prioritize_hospitals
import streamlit.components.v1 as components
import datetime
import pandas as pd

db = DB()

# ---------------- DASHBOARD ----------------

def bank_dashboard():

    st.sidebar.title("🏦 Organ Bank")

    menu = st.sidebar.radio("Menu", [
        "All Requests",
        "Hospital Requests",
        "Emergency Cases",
        "Inventory",
        "Analytics"
    ])

    if menu == "All Requests":
        all_requests()

    elif menu == "Hospital Requests":
        hospital_requests()

    elif menu == "Emergency Cases":
        emergency_cases()

    elif menu == "Inventory":
        inventory()

    elif menu == "Analytics":
        analytics()


# ---------------- ALL REQUESTS ----------------

def all_requests():

    st.title("📋 All Bank Requests")

    st.info(
        "Only emergency organ donations and "
        "hospital organ transfer requests appear here."
    )

    data = db.conn.execute("""
    SELECT username,name,organ,source,status,datetime
    FROM bank_requests
    ORDER BY id DESC
    """).fetchall()

    if data:

        df = pd.DataFrame(
            data,
            columns=[
                "User",
                "Name",
                "Organ",
                "Source",
                "Status",
                "Time"
            ]
        )

        st.dataframe(df)

    else:
        st.info("No requests yet")


# ---------------- HOSPITAL REQUESTS ----------------

def hospital_requests():

    st.title("🏥 AI Hospital Priority Requests")

    st.markdown("""
    <div style='
        background:linear-gradient(90deg,#001f3f,#003366,#0055aa);
        padding:18px;
        border-radius:18px;
        margin-bottom:25px;
        box-shadow:0 0 25px rgba(0,170,255,0.6);
    '>

    <h2 style='color:white;text-align:center;'>
    🤖 AI Hospital Allocation System
    </h2>

    <p style='color:#dddddd;text-align:center;'>
    Emergency + ICU + Distance + Smart Priority Ranking
    </p>

    </div>
    """, unsafe_allow_html=True)

    # ONLY HOSPITAL GENERATED REQUESTS

    data = db.conn.execute("""
    SELECT id,username,name,organ,source,status,datetime
    FROM bank_requests
    WHERE username='Hospital'
    ORDER BY id DESC
    """).fetchall()

    if not data:
        st.info("No Hospital Requests")
        return

    ranked_data = []

    # =====================================
    # AI PRIORITY
    # =====================================

    for row in data:

        try:

            ranked = prioritize_hospitals(
                db,
                row[3]
            )

            ai_score = 75

            for item in ranked:

                if item["hospital_name"] == row[4]:
                    ai_score = item["final_score"]
                    break

        except:
            ai_score = 75

        ranked_data.append({
            "row": row,
            "score": ai_score
        })

    # =====================================
    # SORT BY AI SCORE
    # =====================================

    ranked_data.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # =====================================
    # SHOW AI REQUESTS
    # =====================================

    for index, item in enumerate(ranked_data, start=1):

        row = item["row"]
        score = item["score"]

        if score >= 90:
            priority = "🔴 SUPER PRIORITY"
            border = "#ff2e63"

        elif score >= 75:
            priority = "🟠 HIGH PRIORITY"
            border = "#ffaa00"

        else:
            priority = "🟢 NORMAL PRIORITY"
            border = "#00cc66"

        with st.expander(
            f"#{index} • {row[4]} • {row[3]}"
        ):

            # =====================================
            # AI CIRCLE
            # =====================================

            html_code = f'''

            <style>

            .circle-container {{
                display:flex;
                justify-content:center;
                align-items:center;
                margin-top:10px;
                margin-bottom:20px;
            }}

            .ai-circle {{

                width:150px;
                height:150px;

                border-radius:50%;

                background:
                radial-gradient(circle,
                rgba(0,200,255,0.95) 0%,
                rgba(0,90,255,0.35) 45%,
                rgba(0,0,0,1) 100%);

                display:flex;
                justify-content:center;
                align-items:center;

                color:white;

                font-size:34px;
                font-weight:bold;

                box-shadow:
                0 0 25px #00c3ff,
                0 0 60px #0099ff,
                0 0 120px #0066ff;

                animation:pulse 2s infinite;
            }}

            @keyframes pulse {{

                0% {{
                    transform:scale(1);
                }}

                50% {{
                    transform:scale(1.08);
                }}

                100% {{
                    transform:scale(1);
                }}
            }}

            </style>

            <div class="circle-container">
                <div class="ai-circle">
                    {score}%
                </div>
            </div>

            '''

            components.html(
                html_code,
                height=190
            )

            st.markdown(f"""
            <div style='
                background:rgba(10,15,30,0.96);
                padding:18px;
                border-radius:18px;
                border-left:8px solid {border};
                box-shadow:0 0 20px rgba(0,180,255,0.3);
            '>

            <h3 style='color:white;'>
            🏥 {row[4]}
            </h3>

            <p style='color:#00d0ff;font-size:18px;'>
            🫀 Organ:
            <b>{row[3]}</b>
            </p>

            <p style='color:white;'>
            📌 Status:
            <b>{row[5]}</b>
            </p>

            <p style='color:white;'>
            🤖 AI Score:
            <b>{score}%</b>
            </p>

            <p style='color:white;'>
            🚨 Priority:
            <b>{priority}</b>
            </p>

            <p style='color:#cccccc;'>
            ✔ Emergency Analysis Applied<br>
            ✔ ICU Priority Checked<br>
            ✔ Smart Hospital Ranking Enabled<br>
            ✔ Distance Optimization Applied
            </p>

            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            if col1.button(
                f"Approve {row[0]}",
                key=f"approve_{row[0]}"
            ):
                approve_request(row, "Hospital")

            if col2.button(
                f"Reject {row[0]}",
                key=f"reject_{row[0]}"
            ):
                reject_request(row[0])


# ---------------- EMERGENCY CASES ----------------

def emergency_cases():

    st.title("🚨 Emergency Organ Cases")

    data = db.conn.execute("""
    SELECT id,username,name,organ,source,status,datetime
    FROM bank_requests
    WHERE organ='Multiple Organs'
    ORDER BY id DESC
    """).fetchall()

    if not data:
        st.info("No Emergency Cases")
        return

    for row in data:

        with st.expander(
            f"🚨 {row[2]} • {row[6]}"
        ):

            st.error("Critical Organ Donation Case")

            st.write(f"🏥 Source Hospital: {row[4]}")
            st.write(f"🫀 Organ: {row[3]}")
            st.write(f"📌 Status: {row[5]}")

            col1, col2 = st.columns(2)

            if col1.button(
                f"Approve {row[0]}",
                key=f"emergency_approve_{row[0]}"
            ):
                approve_request(row, "Emergency")

            if col2.button(
                f"Reject {row[0]}",
                key=f"emergency_reject_{row[0]}"
            ):
                reject_request(row[0])


# ---------------- APPROVE ----------------

def approve_request(row, source_type):

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    db.conn.execute("""
    UPDATE bank_requests
    SET status='Approved'
    WHERE id=?
    """, (row[0],))

    # INVENTORY OUT

    db.conn.execute("""
    INSERT INTO inventory
    (organ, quantity, type, source, destination, datetime)
    VALUES (?, ?, 'OUT', ?, ?, ?)
    """, (
        row[3],
        1,
        "Bank",
        row[4],
        now
    ))

    db.conn.commit()


    st.success("✅ Approved & Sent")


# ---------------- REJECT ----------------

def reject_request(req_id):

    db.conn.execute("""
    UPDATE bank_requests
    SET status='Rejected'
    WHERE id=?
    """, (req_id,))

    db.conn.commit()


    st.error("❌ Rejected")


# ---------------- INVENTORY ----------------

def inventory():

    st.title("📦 Inventory System")

    tab1, tab2 = st.tabs(["IN","OUT"])

    with tab1:

        data = db.conn.execute("""
        SELECT organ, quantity, source, datetime
        FROM inventory
        WHERE type='IN'
        """).fetchall()

        if data:

            df = pd.DataFrame(
                data,
                columns=[
                    "Organ",
                    "Qty",
                    "From",
                    "Time"
                ]
            )

            st.table(df)

        else:
            st.info("No IN data")

    with tab2:

        data = db.conn.execute("""
        SELECT organ, quantity, destination, datetime
        FROM inventory
        WHERE type='OUT'
        """).fetchall()

        if data:

            df = pd.DataFrame(
                data,
                columns=[
                    "Organ",
                    "Qty",
                    "To",
                    "Time"
                ]
            )

            st.table(df)

        else:
            st.info("No OUT data")


# ---------------- ANALYTICS ----------------

def analytics():

    st.title("📊 Bank Analytics")

    total = db.conn.execute(
        "SELECT COUNT(*) FROM bank_requests"
    ).fetchone()[0]

    approved = db.conn.execute(
        "SELECT COUNT(*) FROM bank_requests WHERE status='Approved'"
    ).fetchone()[0]

    pending = db.conn.execute(
        "SELECT COUNT(*) FROM bank_requests WHERE status='Pending'"
    ).fetchone()[0]

    rejected = db.conn.execute(
        "SELECT COUNT(*) FROM bank_requests WHERE status='Rejected'"
    ).fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total)
    col2.metric("Approved", approved)
    col3.metric("Pending", pending)
    col4.metric("Rejected", rejected)
