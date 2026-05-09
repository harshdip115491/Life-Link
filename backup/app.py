import streamlit as st

from user import register, login, dashboard as user_dashboard
from hospital import hospital_dashboard
from bank import bank_dashboard
from admin import admin_dashboard
from auth import login_hospital
from utils import set_bg

# ---------------- CONFIG ----------------
st.set_page_config(page_title="LifeLink System", layout="wide")

# ---------------- BACKGROUND ----------------
set_bg("assets/bg.jpg")

# ---------------- SESSION INIT ----------------
if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
    st.session_state.user = None

if "hospital" not in st.session_state:
    st.session_state.hospital = None


# ---------------- SIDEBAR ----------------
st.sidebar.title("💙 LifeLink System")


# =========================================================
# NOT LOGGED IN
# =========================================================
if st.session_state.role is None:

    role = st.sidebar.selectbox("Select Role", ["User", "Hospital", "Bank", "Admin"])

    # ---------------- USER ----------------
    if role == "User":
        option = st.sidebar.radio("Menu", ["Login", "Register"])

        if option == "Register":
            register()

        elif option == "Login":
            login()

    # ---------------- HOSPITAL ----------------
    elif role == "Hospital":
        st.title("🏥 Hospital Login")

        hospital_name = st.selectbox("Select Hospital", [
            "AIIMS Delhi","Apollo Hospital","Fortis Hospital","Kokilaben Hospital",
            "Lilavati Hospital","Tata Memorial","Manipal Hospital","Max Hospital",
            "Narayana Health","Care Hospital","Ruby Hall","Sahyadri Hospital",
            "Wockhardt Hospital","Global Hospital","Medanta","Columbia Asia",
            "Hinduja Hospital","Jaslok Hospital","Yashoda Hospital","Sunshine Hospital"
        ])

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            hosp = login_hospital(username, password)

            if hosp and hosp[1] == hospital_name:
                st.session_state.role = "hospital"
                st.session_state.hospital = hospital_name
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid credentials or hospital mismatch")

    # ---------------- BANK ----------------
    elif role == "Bank":
        st.title("🏦 Organ Bank Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "bank" and password == "123":
                st.session_state.role = "bank"
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # ---------------- ADMIN ----------------
    elif role == "Admin":
        st.title("🛡 Admin Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state.role = "admin"
                st.session_state.user = "admin"   # FIX: ensure session exists
                st.success("Admin Login Successful")
                st.rerun()
            else:
                st.error("Invalid credentials")


# =========================================================
# USER DASHBOARD
# =========================================================
elif st.session_state.role == "user":

    if not st.session_state.user:
        st.session_state.role = None
        st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    user_dashboard()


# =========================================================
# HOSPITAL DASHBOARD
# =========================================================
elif st.session_state.role == "hospital":

    if not st.session_state.hospital:
        st.session_state.role = None
        st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    hospital_dashboard(st.session_state.hospital)



# =========================================================
# BANK DASHBOARD
# =========================================================
elif st.session_state.role == "bank":

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    bank_dashboard()


# =========================================================
# ADMIN DASHBOARD (FIXED CONNECTION)
# =========================================================
elif st.session_state.role == "admin":

    st.sidebar.success("Admin Mode Active")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    admin_dashboard()