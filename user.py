import streamlit as st
from db import DB
from india_data import india
from image_utils import save_image
from search_utils import search, sort_data
from utils import notify
from sound_utils import play_sound
from pdf_utils import generate_certificate_production
from streamlit_cropper import st_cropper
import datetime
import os
from PIL import Image
import pandas as pd

db = DB()

# ---------------- GLOBAL FLAGS ----------------
if "play_login_sound" not in st.session_state:
    st.session_state.play_login_sound = False

if "profile_updated" not in st.session_state:
    st.session_state.profile_updated = False


# ---------------- REGISTER ----------------

def register():
    st.markdown("## 📝 Register")

    if "temp_image" not in st.session_state:
        st.session_state.temp_image = None
    if "img_mode" not in st.session_state:
        st.session_state.img_mode = "None"
    if "reg_cropped" not in st.session_state:
        st.session_state.reg_cropped = None

    with st.form("register"):

        col1, col2 = st.columns(2)

        name = col1.text_input("Full Name")
        dob = col2.date_input(
            "DOB",
            min_value=datetime.date(1901, 1, 1),
            max_value=datetime.date(2080, 12, 31),
            value=None
        )

        gender = col1.selectbox("Gender", ["Male","Female","Other"])
        blood = col2.selectbox("Blood", ["A+","A-","B+","B-","O+","O-","AB+","AB-"])

        aadhaar = col1.text_input("Aadhaar")
        phone = col2.text_input("Phone")

        family = col1.text_input("Emergency Contact")
        email = col2.text_input("Email")

        address = st.text_area("Address")

        colA, colB = st.columns(2)
        state = colA.selectbox("State", list(india.keys()))
        district = colB.selectbox("District", india[state])

        subdistrict = st.text_input("Subdistrict")
        pincode = st.text_input("Pincode")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        st.markdown("### 📸 Profile Image")

        colx, coly, colz = st.columns(3)

        if colx.form_submit_button("📤 Upload Mode"):
            st.session_state.img_mode = "Upload"

        if coly.form_submit_button("📷 Camera Mode"):
            st.session_state.img_mode = "Camera"

        if st.session_state.img_mode != "None":
            if colz.form_submit_button("❌ Cancel"):
                st.session_state.img_mode = "None"
                st.session_state.temp_image = None
                st.session_state.reg_cropped = None

        img_file = None

        if st.session_state.img_mode == "Upload":
            img_file = st.file_uploader("Upload Image", type=["jpg","jpeg","png"])

        elif st.session_state.img_mode == "Camera":
            img_file = st.camera_input("Take Photo")

        if img_file:
            st.session_state.temp_image = img_file

        if st.session_state.img_mode != "None" and st.session_state.temp_image:
            img = Image.open(st.session_state.temp_image)

            cropped_img = st_cropper(
                img,
                realtime_update=True,
                aspect_ratio=(1,1)
            )

            st.session_state.reg_cropped = cropped_img

        submit = st.form_submit_button("Register")

    if submit:

        if not all([name,dob,aadhaar,phone,username,password]):
            st.error("Fill all required fields")
            play_sound("assets/error.mp3")
            return

        c = db.conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? OR aadhaar=? OR phone=?",
                  (username,aadhaar,phone))

        if c.fetchone():
            st.error("Duplicate data")
            play_sound("assets/error.mp3")
            return

        image_path = ""

        if st.session_state.temp_image:
            image_path = save_image(
                st.session_state.temp_image,
                username,
                st.session_state.get("reg_cropped")
            )

        db.conn.execute("""
        INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            username,
            db.hash_password(password),
            name,str(dob),gender,blood,
            aadhaar,phone,family,email,state,district,
            subdistrict,pincode,address,image_path
        ))

        db.conn.commit()

        st.success("✅ Registration Successful")
        play_sound("assets/success.mp3")
        notify()

        st.session_state.temp_image = None
        st.session_state.reg_cropped = None


# ---------------- LOGIN ----------------

def login():
    st.title("🔐 User Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        user = db.conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, db.hash_password(p))
        ).fetchone()

        if user:
            st.session_state.play_login_sound = True
            st.session_state.user = u
            st.session_state.role = "user"
            st.rerun()
        else:
            play_sound("assets/loginerror.mp3")
            st.error("Invalid credentials")


# ---------------- DASHBOARD ----------------

def dashboard():

    if st.session_state.get("play_login_sound"):
        play_sound("assets/login.mp3")
        st.session_state.play_login_sound = False

    user = st.session_state.user
    data = db.conn.execute("SELECT * FROM users WHERE username=?", (user,)).fetchone()

    st.sidebar.title("User Panel")

    menu = st.sidebar.radio("Menu", [
        "Home","Profile","Request Organ","My Requests",
        "Donate Organ","Emergency","Analytics","Logout"
    ])

    if menu == "Home":
        home(data)
    elif menu == "Profile":
        profile(data)
    elif menu == "Request Organ":
        request_organ(data)
    elif menu == "My Requests":
        my_requests(user)
    elif menu == "Donate Organ":
        donate(data)
    elif menu == "Emergency":
        emergency(data)
    elif menu == "Analytics":
        analytics(user)
    elif menu == "Logout":
        st.session_state.clear()
        st.rerun()


# ---------------- HOME ----------------

def home(data):
    st.title("💙 LIFE + LINK")

    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown("""
        ### 🫀 Organ Donation Awareness
        - 1 donor saves 8 lives  
        - 5 lakh+ waiting patients  
        - <1% donation rate  
        """)

    with col2:
        if data[15] and os.path.exists(data[15]):
            st.image(data[15], width="stretch")


# ---------------- PROFILE ----------------

def profile(data):
    st.title("👤 Profile")

    # ✅ SHOW SUCCESS AFTER RERUN
    if st.session_state.get("profile_updated"):
        st.success("✅ Profile Updated")
        play_sound("assets/success.mp3")
        notify()
        st.session_state.profile_updated = False

    if "profile_img_mode" not in st.session_state:
        st.session_state.profile_img_mode = "None"
    if "profile_temp_img" not in st.session_state:
        st.session_state.profile_temp_img = None
    if "profile_cropped" not in st.session_state:
        st.session_state.profile_cropped = None

    if data[15] and os.path.exists(data[15]):
        st.image(data[15], width=150)

    st.markdown("### 📸 Update Profile Image")

    col1, col2, col3 = st.columns(3)

    if col1.button("📤 Upload"):
        st.session_state.profile_img_mode = "Upload"

    if col2.button("📷 Camera"):
        st.session_state.profile_img_mode = "Camera"

    if st.session_state.profile_img_mode != "None":
        if col3.button("❌ Cancel"):
            st.session_state.profile_img_mode = "None"
            st.session_state.profile_temp_img = None
            st.session_state.profile_cropped = None

    img_file = None

    if st.session_state.profile_img_mode == "Upload":
        img_file = st.file_uploader("Upload Image", type=["jpg","jpeg","png"], key="profile_upload")

    elif st.session_state.profile_img_mode == "Camera":
        img_file = st.camera_input("Take Photo")

    if img_file:
        st.session_state.profile_temp_img = img_file

    if st.session_state.profile_img_mode != "None" and st.session_state.profile_temp_img:
        img = Image.open(st.session_state.profile_temp_img)

        cropped_img = st_cropper(
            img,
            realtime_update=True,
            aspect_ratio=(1,1)
        )

        st.session_state.profile_cropped = cropped_img

    with st.form("update"):
        name = st.text_input("Name", data[2])
        phone = st.text_input("Phone", data[7])
        email = st.text_input("Email", data[9])
        address = st.text_area("Address", data[14])
        password = st.text_input("New Password", type="password")

        submit = st.form_submit_button("Update Profile")

    if submit:

        new_image_path = data[15]

        if st.session_state.profile_cropped:
            new_image_path = save_image(
                st.session_state.profile_temp_img,
                data[0],
                st.session_state.profile_cropped
            )

        db.conn.execute("""
        UPDATE users SET name=?, phone=?, email=?, address=?, password=?, image=?
        WHERE username=?
        """, (
            name,
            phone,
            email,
            address,
            db.hash_password(password) if password else data[1],
            new_image_path,
            data[0]
        ))

        db.conn.commit()

        # ✅ FIX: use flag instead of instant message
        st.session_state.profile_updated = True

        st.session_state.profile_temp_img = None
        st.session_state.profile_cropped = None
        st.session_state.profile_img_mode = "None"

        st.rerun()


# ---------------- REQUEST ----------------

def request_organ(data):
    st.title("🫀 Request Organ")

    hospitals = [h[0] for h in db.conn.execute("SELECT name FROM hospitals")]

    organ = st.selectbox("Organ", ["Heart","Kidney","Liver"])
    hospital = st.selectbox("Hospital", hospitals)
    priority = st.selectbox("Priority", ["High","Medium","Low"])
    note = st.text_area("Note")

    if st.button("Submit"):
        dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        db.conn.execute("""
        INSERT INTO requests (username,name,organ,hospital,priority,note,datetime)
        VALUES (?,?,?,?,?,?,?)
        """, (data[0],data[2],organ,hospital,priority,note,dt))

        db.conn.commit()

        st.success("Submitted")
        play_sound("assets/success.mp3")
        notify()


# ---------------- MY REQUESTS ----------------

def my_requests(user):
    st.title("📄 My Requests")

    data = db.conn.execute("""
    SELECT id, organ, hospital, status, datetime FROM requests
    WHERE username=?
    """, (user,)).fetchall()

    st.table(data)


# ---------------- DONATE ----------------

def donate(data):
    st.title("❤️ Donate Organ")

    organ = st.selectbox("Organ", ["Heart","Kidney","Liver","Eyes"])

    if st.button("Donate"):

        date = datetime.datetime.now().strftime("%d/%m/%Y")

        db.conn.execute("""
        INSERT INTO donations (username,name,organ,date)
        VALUES (?,?,?,?)
        """, (data[0],data[2],organ,date))

        db.conn.commit()

        play_sound("assets/success.mp3")
        notify()

        cert_data = {
            "name": data[2],
            "hospital": "LifeLink Medical System",
            "cause": "Organ Donation (Voluntary)",
            "date": date
        }

        pdf_path, cert_id = generate_certificate_production(
            cert_data,
            data[0],
            organ
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 Download Certificate",
                f,
                file_name=f"{cert_id}.pdf",
                mime="application/pdf"
            )


# ---------------- EMERGENCY ----------------

def emergency(data):
    st.title("🚨 Emergency")

    place = st.selectbox("Place", ["Home","Hospital"])
    reason = st.text_area("Reason")

    if st.button("Submit Emergency"):
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        db.conn.execute("""
        INSERT INTO emergency (username,name,place,reason,datetime,status)
        VALUES (?,?,?,?,?,?)
        """, (data[0],data[2],place,reason,now,"Pending"))

        db.conn.commit()

        st.success("Emergency Sent")
        play_sound("assets/success.mp3")


# ---------------- ANALYTICS ----------------

def analytics(user):
    st.title("📊 Analytics")

    data = db.conn.execute("""
    SELECT organ, COUNT(*) FROM requests
    WHERE username=? GROUP BY organ
    """, (user,)).fetchall()

    if data:
        df = pd.DataFrame(data, columns=["Organ","Count"])
        st.bar_chart(df.set_index("Organ"))