import streamlit as st
import base64
import os
import uuid


# ---------------- PLAY SOUND ----------------
    if not os.path.exists(path):
        return

    with open(path, "rb") as f:
        data = f.read()

    b64 = base64.b64encode(data).decode()

    st.markdown(f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)


# ---------------- TRIGGER SOUND ----------------
    if "sound_queue" not in st.session_state:
        st.session_state.sound_queue = []

    st.session_state.sound_queue.append({
        "path": path,
        "id": str(uuid.uuid4())
    })


# ---------------- PROCESS SOUND ----------------
    if "sound_queue" not in st.session_state:
        return

    for item in st.session_state.sound_queue:

    st.session_state.sound_queue = []
