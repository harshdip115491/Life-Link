import streamlit as st
from db import DB
from sound_utils import play_sound
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
    st.title("📋 All Requests")

    data = db.conn.execute("""
    SELECT username,name,organ,source,status,datetime 
    FROM bank_requests
    """).fetchall()

    if data:
        df = pd.DataFrame(data, columns=["User","Name","Organ","Source","Status","Time"])
        st.dataframe(df)
    else:
        st.info("No requests yet")


# ---------------- HOSPITAL REQUESTS ----------------

def hospital_requests():
    st.title("🏥 Hospital Requests")

    data = db.conn.execute("""
    SELECT id,username,name,organ,source,status,datetime 
    FROM bank_requests WHERE username='Hospital'
    """).fetchall()

    for row in data:
        with st.expander(f"{row[3]} - {row[2]} ({row[6]})"):

            st.write(f"Organ: {row[3]}")
            st.write(f"Hospital: {row[4]}")
            st.write(f"Status: {row[5]}")

            col1, col2 = st.columns(2)

            if col1.button(f"Approve {row[0]}"):
                approve_request(row, "Hospital")

            if col2.button(f"Reject {row[0]}"):
                reject_request(row[0])


# ---------------- EMERGENCY CASES ----------------

def emergency_cases():
    st.title("🚨 Emergency Cases")

    data = db.conn.execute("""
    SELECT id,username,name,organ,source,status,datetime 
    FROM bank_requests WHERE organ='Multiple'
    """).fetchall()

    for row in data:
        with st.expander(f"{row[2]} ({row[6]})"):

            st.write(f"Source: {row[4]}")
            st.write(f"Status: {row[5]}")

            col1, col2 = st.columns(2)

            if col1.button(f"Approve {row[0]}"):
                approve_request(row, "Emergency")

            if col2.button(f"Reject {row[0]}"):
                reject_request(row[0])


# ---------------- APPROVE ----------------

def approve_request(row, source_type):

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # UPDATE STATUS
    db.conn.execute("""
    UPDATE bank_requests SET status='Approved' WHERE id=?
    """, (row[0],))

    # INVENTORY OUT (send to hospital)
    db.conn.execute("""
    INSERT INTO inventory (organ, quantity, type, source, destination, datetime)
    VALUES (?, ?, 'OUT', ?, ?, ?)
    """, (row[3], 1, "Bank", row[4], now))

    db.conn.commit()

    play_sound("assets/success.mp3")
    st.success("Approved & Sent")


# ---------------- REJECT ----------------

def reject_request(req_id):
    db.conn.execute("""
    UPDATE bank_requests SET status='Rejected' WHERE id=?
    """, (req_id,))

    db.conn.commit()

    play_sound("assets/error.mp3")
    st.error("Rejected")


# ---------------- INVENTORY ----------------

def inventory():
    st.title("📦 Inventory System")

    tab1, tab2 = st.tabs(["IN","OUT"])

    with tab1:
        data = db.conn.execute("""
        SELECT organ, quantity, source, datetime FROM inventory
        WHERE type='IN'
        """).fetchall()

        if data:
            df = pd.DataFrame(data, columns=["Organ","Qty","From","Time"])
            st.table(df)
        else:
            st.info("No IN data")

    with tab2:
        data = db.conn.execute("""
        SELECT organ, quantity, destination, datetime FROM inventory
        WHERE type='OUT'
        """).fetchall()

        if data:
            df = pd.DataFrame(data, columns=["Organ","Qty","To","Time"])
            st.table(df)
        else:
            st.info("No OUT data")


# ---------------- ANALYTICS ----------------

def analytics():
    st.title("📊 Bank Analytics")

    total = db.conn.execute("SELECT COUNT(*) FROM bank_requests").fetchone()[0]
    approved = db.conn.execute("SELECT COUNT(*) FROM bank_requests WHERE status='Approved'").fetchone()[0]
    pending = db.conn.execute("SELECT COUNT(*) FROM bank_requests WHERE status='Pending'").fetchone()[0]
    rejected = db.conn.execute("SELECT COUNT(*) FROM bank_requests WHERE status='Rejected'").fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total)
    col2.metric("Approved", approved)
    col3.metric("Pending", pending)
    col4.metric("Rejected", rejected)