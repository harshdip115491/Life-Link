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
    user = db.conn.execute("SELECT * FROM users WHERE username=?", (row[1],)).fetchone()

    st.write(f"👤 Name: {user[2]}")
    st.write(f"🩸 Blood: {user[5]}")
    st.write(f"📞 Phone: {user[7]}")
    st.write(f"📍 Address: {user[14]}")
    st.write(f"🫀 Organ Needed: {row[3]}")
    st.write(f"📌 Status: {row[7]}")

    st.subheader("🤖 AI Matching Donors")
    matches = match_organ(db, row[3], user[5])
    st.write(matches if matches else "No matches")

    col1, col2, col3 = st.columns(3)

    if col1.button(f"Approve {row[0]}"):
        update_status(row[0], "Approved")

    if col2.button(f"Reject {row[0]}"):
        update_status(row[0], "Rejected")

    if col3.button(f"Pending {row[0]}"):
        update_status(row[0], "Pending")

    if st.checkbox(f"Mark as Deceased (ID {row[0]})"):
        death_certificate(user, hospital)


# ---------------- UPDATE STATUS ----------------

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


# ---------------- SEARCH USER ----------------

def search_user():
    st.title("🔎 Search User")

    aadhaar = st.text_input("Enter Aadhaar")

    if st.button("Search"):
        user = db.conn.execute("SELECT * FROM users WHERE aadhaar=?", (aadhaar,)).fetchone()

        if user:
            st.write(user)
        else:
            st.error("Not found")


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
