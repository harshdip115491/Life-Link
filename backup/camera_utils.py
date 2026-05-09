import streamlit as st
from PIL import Image
import numpy as np
import cv2
import os
import time

# ---------------- FACE DETECTION ----------------
def detect_best_face(image):
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return None

    # choose largest face
    best = max(faces, key=lambda f: f[2] * f[3])
    x, y, w, h = best

    return (x, y, w, h)


# ---------------- PASSPORT CROP ----------------
def passport_crop(image, face):
    x, y, w, h = face

    cx = x + w // 2
    cy = y + h // 2

    size = int(max(w, h) * 2)

    left = max(cx - size // 2, 0)
    top = max(cy - size // 2, 0)
    right = min(cx + size // 2, image.width)
    bottom = min(cy + size // 2, image.height)

    return image.crop((left, top, right, bottom))


# ---------------- MAIN CAMERA FUNCTION ----------------
def capture_image(username):

    st.markdown("## 📸 Camera Capture")

    if "cam_stage" not in st.session_state:
        st.session_state.cam_stage = "capture"

    if "captured_img" not in st.session_state:
        st.session_state.captured_img = None

    # ---------------- STAGE 1: CAPTURE ----------------
    if st.session_state.cam_stage == "capture":

        st.info("Allow camera access (Supports USB Webcam also)")

        cam = st.camera_input("Take Photo")

        if cam:
            img = Image.open(cam)
            st.session_state.captured_img = img
            st.session_state.cam_stage = "preview"
            st.rerun()

        return None

    # ---------------- STAGE 2: PREVIEW ----------------
    elif st.session_state.cam_stage == "preview":

        img = st.session_state.captured_img

        st.image(img, caption="Preview", use_column_width=True)

        # -------- AUTO FACE DETECTION --------
        face = detect_best_face(img)

        if face:
            st.success("Face Detected ✅")

            cropped = passport_crop(img, face)
            st.image(cropped, caption="Auto Passport Crop")

        else:
            st.warning("No Face Detected")
            cropped = img

        # -------- BUTTONS --------
        col1, col2, col3 = st.columns(3)

        # RETAKE
        if col1.button("🔄 Retake"):
            st.session_state.cam_stage = "capture"
            st.session_state.captured_img = None
            st.rerun()

        # EDIT (manual crop)
        if col2.button("✂️ Edit"):
            st.session_state.cam_stage = "edit"
            st.rerun()

        # SAVE
        if col3.button("✅ Save"):

            filename = f"{username}_{int(time.time())}.jpg"
            path = os.path.join("user_images", filename)

            cropped.save(path)

            st.success("Saved Successfully")
            st.session_state.cam_stage = "capture"
            st.session_state.captured_img = None

            return path

    # ---------------- STAGE 3: EDIT ----------------
    elif st.session_state.cam_stage == "edit":

        img = st.session_state.captured_img

        st.subheader("✂️ Manual Crop")

        left = st.slider("Left", 0, img.width, 0)
        right = st.slider("Right", 0, img.width, img.width)
        top = st.slider("Top", 0, img.height, 0)
        bottom = st.slider("Bottom", 0, img.height, img.height)

        # FIX ERROR: right < left
        if right <= left:
            right = left + 1
        if bottom <= top:
            bottom = top + 1

        cropped = img.crop((left, top, right, bottom))

        st.image(cropped, caption="Edited")

        col1, col2 = st.columns(2)

        if col1.button("🔄 Retake"):
            st.session_state.cam_stage = "capture"
            st.session_state.captured_img = None
            st.rerun()

        if col2.button("✅ Save"):
            filename = f"{username}_{int(time.time())}.jpg"
            path = os.path.join("user_images", filename)

            cropped.save(path)

            st.success("Saved Successfully")
            st.session_state.cam_stage = "capture"
            st.session_state.captured_img = None

            return path

    return None