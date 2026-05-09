import base64
import streamlit as st

def set_bg(image):
    with open(image, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{data}");
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

def notify():
    st.balloons()
    st.success("Action Completed ✅")