import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
DB = "lifelink.db"


# ---------------- LOAD DATA ----------------
def load_data():
    conn = sqlite3.connect(DB)

    users = pd.read_sql("SELECT * FROM users", conn)
    hospitals = pd.read_sql("SELECT * FROM hospitals", conn)
    requests = pd.read_sql("SELECT * FROM requests", conn)
    bank = pd.read_sql("SELECT * FROM bank_requests", conn)
    inventory = pd.read_sql("SELECT * FROM inventory", conn)
    emergency = pd.read_sql("SELECT * FROM emergency", conn)

    conn.close()
    return users, hospitals, requests, bank, inventory, emergency


# ---------------- DASHBOARD ----------------
def admin_dashboard():

    st.title("📊 LifeLink Analytics Dashboard (NOTTO Style)")

    users, hospitals, requests, bank, inventory, emergency = load_data()

    # ---------------- TOP METRICS ----------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👤 Total Users", len(users))
    col2.metric("🏥 Hospitals", len(hospitals))
    col3.metric("📄 Requests", len(requests))
    col4.metric("🚨 Emergencies", len(emergency))

    st.divider()

    # ---------------- ORGAN DEMAND ----------------
    st.subheader("🫀 Organ Demand (Requests)")

    if not requests.empty:
        organ_count = requests["organ"].value_counts()

        fig = plt.figure()
        organ_count.plot(kind="bar")
        plt.title("Organ Requests")
        plt.xlabel("Organ")
        plt.ylabel("Count")
        st.pyplot(fig)

    # ---------------- BANK SUPPLY ----------------
    st.subheader("🏦 Organ Supply (Bank)")

    if not bank.empty:
        bank_count = bank["organ"].value_counts()

        fig = plt.figure()
        bank_count.plot(kind="bar")
        plt.title("Bank Supply")
        plt.xlabel("Organ")
        plt.ylabel("Count")
        st.pyplot(fig)

    # ---------------- INVENTORY FLOW ----------------
    st.subheader("🔄 Inventory Movement")

    if not inventory.empty:
        inv = inventory["type"].value_counts()

        fig = plt.figure()
        inv.plot(kind="bar")
        plt.title("IN vs OUT")
        st.pyplot(fig)

    # ---------------- REQUEST TREND ----------------
    st.subheader("📈 Request Trend Over Time")

    if not requests.empty:
        requests["datetime"] = pd.to_datetime(requests["datetime"], errors='coerce')
        trend = requests.groupby(requests["datetime"].dt.date).size()

        fig = plt.figure()
        trend.plot()
        plt.title("Daily Requests")
        st.pyplot(fig)

    # ---------------- EMERGENCY STATUS ----------------
    st.subheader("🚨 Emergency Cases")

    if not emergency.empty:
        status = emergency["status"].value_counts()

        fig = plt.figure()
        status.plot(kind="bar")
        plt.title("Emergency Status")
        st.pyplot(fig)

    # ---------------- HOSPITAL ACTIVITY ----------------
    st.subheader("🏥 Hospital Activity")

    if not requests.empty:
        hosp = requests["hospital"].value_counts().head(10)

        fig = plt.figure()
        hosp.plot(kind="bar")
        plt.title("Top Hospitals by Requests")
        st.pyplot(fig)

    # ---------------- RAW DATA (OPTIONAL) ----------------
    with st.expander("📂 View Raw Data"):
        st.write("Users", users)
        st.write("Requests", requests)
        st.write("Bank", bank)
        st.write("Inventory", inventory)
