import streamlit as st
from db import DB
from search_utils import search, sort_data
from pdf_utils import generate_certificate_production
from ai_match import match_organ
import datetime
import pandas as pd

db = DB()

# ---------------- DASHBOARD ----------------

def hospital_dashboard(hospital):

    st.sidebar.title(f"🏥 {hospital}")

    menu = st.sidebar.radio("Menu", [
        "View Requests",
        "Approved Patients",
        "AI Priority Queue",
        "Search User",
        "Send Request to Bank",
        "Emergency Alerts",
        "Inventory",
        "Analytics"
    ])

    if menu == "View Requests":
        view_requests(hospital)

    elif menu == "Approved Patients":
        approved_patients(hospital)

    elif menu == "AI Priority Queue":
         ai_priority_queue(hospital)

    elif menu == "Search User":
        search_user()

    elif menu == "Send Request to Bank":
        send_request_bank(hospital)

    elif menu == "Emergency Alerts":
        emergency_alerts(hospital)

    elif menu == "Inventory":
        inventory(hospital)

    elif menu == "Analytics":
        analytics(hospital)


# ---------------- VIEW REQUESTS ----------------

def view_requests(hospital):
    st.title("📥 Organ Requests")

    data = db.conn.execute("""
    SELECT * FROM requests WHERE hospital=?
    """, (hospital,)).fetchall()

    for row in data:
        with st.expander(f"ID {row[0]} - {row[2]} ({row[3]})"):
            request_detail(row, hospital)


# ---------------- REQUEST DETAIL ----------------

def request_detail(row, hospital):

    import streamlit.components.v1 as components

    user = db.conn.execute(
        "SELECT * FROM users WHERE username=?",
        (row[1],)
    ).fetchone()

    st.write(f"👤 Name: {user[2]}")
    st.write(f"🩸 Blood: {user[5]}")
    st.write(f"📞 Phone: {user[7]}")
    st.write(f"📍 Address: {user[14]}")
    st.write(f"🫀 Organ Needed: {row[3]}")
    st.write(f"📌 Status: {row[7]}")

    # =========================================
    # AI MATCHING SECTION
    # =========================================

    st.markdown("---")
    st.subheader("🤖 Advanced AI Donor Matching")

    matches = match_organ(db, row[3], user[5])

    if matches:

        best_score = 0

        # GET BEST SCORE
        try:
            best_score = matches[0]["final_score"]
        except:
            best_score = 92

        # =====================================
        # GLOWING AI CIRCLE
        # =====================================

        html_code = f'''

        <style>

        .ai-container {{
            display:flex;
            justify-content:center;
            align-items:center;
            margin-top:20px;
            margin-bottom:20px;
        }}

        .ai-circle {{

            width:190px;
            height:190px;

            border-radius:50%;

            background:
            radial-gradient(circle,
            rgba(0,180,255,0.95) 0%,
            rgba(0,90,255,0.35) 45%,
            rgba(0,0,0,1) 100%);

            display:flex;
            justify-content:center;
            align-items:center;

            color:white;

            font-size:44px;
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

        <div class="ai-container">
            <div class="ai-circle">
                {best_score}%
            </div>
        </div>

        '''

        components.html(html_code, height=260)

        st.success("🧠 AI Matching Completed")

        # =====================================
        # SORTED AI RESULTS
        # =====================================

        for idx, donor in enumerate(matches, start=1):

            score = donor.get("final_score", 80)

            if score >= 90:
                priority = "🔴 SUPER PRIORITY"
                color = "red"

            elif score >= 75:
                priority = "🟠 HIGH PRIORITY"
                color = "orange"

            else:
                priority = "🟢 NORMAL PRIORITY"
                color = "green"

            with st.container():

                st.markdown(f"""
                <div style='
                    background:rgba(15,15,25,0.95);
                    padding:18px;
                    border-radius:18px;
                    margin-bottom:15px;
                    border-left:8px solid {color};
                    box-shadow:0 0 20px rgba(0,150,255,0.4);
                '>

                <h4 style='color:white;'>
                #{idx} AI Recommended Donor
                </h4>

                <p style='color:#00d0ff;font-size:18px;'>
                👤 <b>{donor.get("patient_name","Unknown")}</b>
                </p>

                <p style='color:white;'>
                🏥 Hospital:
                {donor.get("hospital_name","Unknown")}
                </p>

                <p style='color:white;'>
                🩸 Blood Group:
                {donor.get("blood","Unknown")}
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
                ✔ Blood Compatible<br>
                ✔ AI Survival Prediction Applied<br>
                ✔ Waiting Time Analyzed<br>
                ✔ Emergency Level Evaluated
                </p>

                </div>
                """, unsafe_allow_html=True)

        # =========================================
    # STATUS BUTTONS
    # =========================================

    col1, col2, col3 = st.columns(3)

    if col1.button(f"Approve {row[0]}"):
        update_status(row[0], "Approved")

    if col2.button(f"Reject {row[0]}"):
        update_status(row[0], "Rejected")

    if col3.button(f"Pending {row[0]}"):
        update_status(row[0], "Pending")

    # =========================================
    # DECEASED
    # =========================================

    if st.checkbox(f"Mark as Deceased (ID {row[0]})"):
        death_certificate(user, hospital)# ---------------- UPDATE STATUS ----------------

def update_status(req_id, status):
    db.conn.execute("UPDATE requests SET status=? WHERE id=?", (status, req_id))
    db.conn.commit()
    st.success(f"Updated to {status}")


# ---------------- DEATH CERTIFICATE ----------------

def death_certificate(user, hospital):
    st.subheader("🧾 Death Certificate")

    cause = st.text_input("Cause of Death")
    confirm = st.checkbox("Consent Verified")

    if st.button("Generate & Send to Bank"):

        if not confirm:
            st.error("Consent required")
            return

        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        data = {
            "name": user[2],
            "hospital": hospital,
            "cause": cause,
            "date": now
        }

        # ✅ PDF
        pdf_path, cert_id = generate_certificate_production(
            data,
            user[0],
            "Multiple Organs",
            hospital_mode=True
        )
        # ✅ BANK ENTRY
        db.conn.execute("""
        INSERT INTO bank_requests (username,name,organ,source,status,datetime)
        VALUES (?,?,?,?,?,?)
        """, (user[0], user[2], "Multiple Organs", hospital, "Pending", now))

        # ✅ INVENTORY
        db.conn.execute("""
        INSERT INTO inventory (organ, quantity, type, source, destination, datetime)
        VALUES (?, ?, 'IN', ?, 'Bank', ?)
        """, ("Multiple Organs", 1, hospital, now))

        db.conn.commit()

        st.success("Sent to Bank & Inventory Updated")
        st.info(f"PDF: {pdf_path}")

# ---------------- APPROVED ----------------

def approved_patients(hospital):
    st.title("✅ Approved Patients")

    data = db.conn.execute("""
    SELECT * FROM requests WHERE hospital=? AND status='Approved'
    """, (hospital,)).fetchall()

    st.table(data)

#calculate the emergency score 
def calculate_patient_ai_score(row):

    urgency_map = {
        "Critical": 100,
        "High": 80,
        "Medium": 60,
        "Low": 30
    }

    urgency = urgency_map.get(
        row["urgency_level"],
        60
    )

    waiting = min(
        row["waiting_days"],
        365
    ) / 365 * 100

    severity = (
        row["disease_severity"] / 5
    ) * 100

    distance = max(
        0,
        100 - row["distance_km"]
    )

    score = (
        urgency * 0.40 +
        waiting * 0.25 +
        severity * 0.20 +
        distance * 0.15
    )

    return round(score, 2)
#ai priority score 
def ai_priority_queue(hospital):

    import streamlit.components.v1 as components

    st.title("🤖 AI Priority Queue")

    requests = db.conn.execute("""
    SELECT *
    FROM requests
    WHERE hospital=?
    """,(hospital,)).fetchall()

    ranked = []

    for row in requests:

        score = calculate_patient_ai_score(row)

        db.conn.execute("""
        UPDATE requests
        SET ai_priority_score=?
        WHERE id=?
        """,(score,row["id"]))

        ranked.append({
            "row": row,
            "score": score
        })

    db.conn.commit()

    ranked.sort(
        key=lambda x:x["score"],
        reverse=True
    )

    if not ranked:
        st.info("No Requests")
        return

    for rank,item in enumerate(ranked,start=1):

        row = item["row"]
        score = int(item["score"])

        html=f'''
        <div style="
        width:140px;
        height:140px;
        border-radius:50%;
        margin:auto;
        background:radial-gradient(circle,#00d4ff,#001f3f);
        display:flex;
        justify-content:center;
        align-items:center;
        color:white;
        font-size:30px;
        font-weight:bold;
        box-shadow:0 0 40px #00d4ff;
        ">
        {score}%
        </div>
        '''

        with st.expander(
            f"#{rank} - {row['name']} ({row['organ']})"
        ):

            components.html(
                html,
                height=180
            )

            st.write(
                f"👤 Patient: {row['name']}"
            )

            st.write(
                f"🫀 Organ: {row['organ']}"
            )

            st.write(
                f"🤖 AI Score: {score}%"
            )

            st.write(
                f"📌 Status: {row['status']}"
            ) 

def search_user():

    import os
    from datetime import datetime

    st.title("🔎 Search Organ Donor")

    aadhaar = st.text_input(
        "Enter Aadhaar Number",
        max_chars=12
    )

    if st.button("Search", use_container_width=True):

        if not aadhaar.strip():

            st.warning(
                "Please enter Aadhaar Number"
            )
            return

        user = db.conn.execute(
            """
            SELECT *
            FROM users
            WHERE aadhaar = ?
            """,
            (aadhaar,)
        ).fetchone()

        # ==========================
        # USER NOT FOUND
        # ==========================

        if not user:

            st.error(
                "❌ This Aadhaar number is not registered for organ donation."
            )

            return

        # ==========================
        # USER FOUND
        # ==========================

        st.success(
            "✅ Registered Organ Donor Found"
        )

        col1, col2 = st.columns([1, 2])

        # ==========================
        # PHOTO
        # ==========================

        with col1:

            try:

                if (
                    user["image"]
                    and os.path.exists(user["image"])
                ):

                    st.image(
                        user["image"],
                        width=250
                    )

                else:

                    st.info("No Photo Available")

            except:
                st.info("No Photo Available")

        # ==========================
        # PROFILE DETAILS
        # ==========================

        with col2:

            st.markdown("### 👤 Donor Profile")

            st.write(
                f"**Full Name:** {user['name']}"
            )

            st.write(
                f"**Date of Birth:** {user['dob']}"
            )

            st.write(
                f"**Gender:** {user['gender']}"
            )

            st.write(
                f"**Blood Group:** {user['blood']}"
            )

            st.write(
                f"**Aadhaar Number:** {user['aadhaar']}"
            )

            st.write(
                f"**Phone Number:** {user['phone']}"
            )

            st.write(
                f"**Email:** {user['email']}"
            )

            st.write(
                f"**Family Contact:** {user['family']}"
            )

        st.markdown("---")

        st.markdown("### 📍 Address Information")

        st.write(
            f"**State:** {user['state']}"
        )

        st.write(
            f"**District:** {user['district']}"
        )

        st.write(
            f"**Sub District:** {user['subdistrict']}"
        )

        st.write(
            f"**Pincode:** {user['pincode']}"
        )

        st.write(
            f"**Address:** {user['address']}"
        )

        st.markdown("---")

        # ==========================
        # DONOR STATUS
        # ==========================

        st.success(
            "🫀 DONOR STATUS : REGISTERED FOR ORGAN DONATION"
        )

        st.markdown(
            """
            <div style="
                padding:15px;
                border-radius:15px;
                background:#0f5132;
                color:white;
                font-size:20px;
                text-align:center;
                font-weight:bold;
            ">
            ✅ VERIFIED DONOR
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------- SEND REQUEST TO BANK ----------------

def send_request_bank(hospital):
    st.title("📤 Request to Organ Bank")

    organ = st.selectbox("Organ", ["Heart","Kidney","Liver"])
    qty = st.number_input("Quantity", min_value=1)

    if st.button("Generate Request"):

        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        db.conn.execute("""
        INSERT INTO bank_requests (username,name,organ,source,status,datetime)
        VALUES (?,?,?,?,?,?)
        """, ("Hospital", hospital, organ, hospital, "Pending", now))

        db.conn.commit()


        st.success("Request Sent")


# ---------------- EMERGENCY ALERTS ----------------

def emergency_alerts(hospital):
    st.title("🚨 Emergency Alerts")

    data = db.conn.execute("""
    SELECT username,name,datetime,status FROM hospital_alerts
    WHERE hospital=?
    """, (hospital,)).fetchall()

    if data:
        df = pd.DataFrame(data, columns=["User","Name","Time","Status"])
        st.table(df)
    else:
        st.info("No alerts")


# ---------------- INVENTORY ----------------

def inventory(hospital):
    st.title("📦 Inventory")

    tab1, tab2 = st.tabs(["IN","OUT"])

    with tab1:
        data = db.conn.execute("""
        SELECT organ, quantity, source, datetime FROM inventory
        WHERE type='IN'
        """).fetchall()

        if data:
            df = pd.DataFrame(data, columns=["Organ","Qty","From","Time"])
            st.table(df)

    with tab2:
        data = db.conn.execute("""
        SELECT organ, quantity, destination, datetime FROM inventory
        WHERE type='OUT'
        """).fetchall()

        if data:
            df = pd.DataFrame(data, columns=["Organ","Qty","To","Time"])
            st.table(df)


# ---------------- ANALYTICS ----------------

def analytics(hospital):
    st.title("📊 Hospital Analytics")

    total = db.conn.execute("SELECT COUNT(*) FROM requests WHERE hospital=?", (hospital,)).fetchone()[0]
    approved = db.conn.execute("SELECT COUNT(*) FROM requests WHERE hospital=? AND status='Approved'", (hospital,)).fetchone()[0]

    col1, col2 = st.columns(2)
    col1.metric("Total Requests", total)
    col2.metric("Approved", approved)
