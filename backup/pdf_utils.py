import os
import uuid
import qrcode
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ---------------- ORGAN FORMAT ----------------
def format_organ(organ):
    if isinstance(organ, list):
        organ = ", ".join(organ)

    organ = organ.lower()

    if "heart" in organ:
        return "❤️ Heart"
    elif "kidney" in organ:
        return "🫀 Kidney"
    elif "liver" in organ:
        return "🫁 Liver"
    elif "eye" in organ:
        return "👁 Eye"
    else:
        return f"🧬 {organ.title()}"


# ---------------- CERTIFICATE ID ----------------
def generate_cert_id():
    return "LL-" + datetime.now().strftime("%Y%m%d") + "-" + str(uuid.uuid4())[:6].upper()


# ---------------- QR VERIFICATION LINK ----------------
def build_verification_url(cert_id):
    return f"https://lifelink.verify/certificate/{cert_id}"


# ---------------- MAIN FUNCTION ----------------
def generate_certificate_production(data, username, organ, hospital_mode=False):

    os.makedirs("certificates", exist_ok=True)
    os.makedirs("certificates/qr", exist_ok=True)

    cert_id = generate_cert_id()

    filename = f"certificates/{cert_id}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    content = []

    # ---------------- HEADER ----------------
    content.append(Paragraph(
        "<b><font size=18 color='darkred'>LIFELINK ORGAN DONATION CERTIFICATE</font></b>",
        styles["Title"]
    ))

    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Certificate ID:</b> {cert_id}", styles["Normal"]))
    content.append(Paragraph(f"<b>Generated Date:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    content.append(Spacer(1, 15))

    # ---------------- USER INFO ----------------
    content.append(Paragraph(f"<b>Name:</b> {data.get('name')}", styles["Normal"]))
    content.append(Paragraph(f"<b>Username:</b> {username}", styles["Normal"]))
    content.append(Paragraph(f"<b>Hospital:</b> {data.get('hospital', 'N/A')}", styles["Normal"]))
    content.append(Paragraph(f"<b>Cause:</b> {data.get('cause', 'Organ Donation')}", styles["Normal"]))

    # ---------------- ORGAN ----------------
    organ_display = format_organ(organ)
    content.append(Paragraph(f"<b>Organ Donated:</b> {organ_display}", styles["Normal"]))

    content.append(Spacer(1, 20))

    # ---------------- QR (VERIFICATION) ----------------
    verify_url = build_verification_url(cert_id)

    qr = qrcode.make(verify_url)
    qr_path = f"certificates/qr/{cert_id}.png"
    qr.save(qr_path)

    content.append(Paragraph("<b>Scan QR for Verification</b>", styles["Normal"]))
    content.append(Image(qr_path, width=120, height=120))

    content.append(Spacer(1, 20))

    # ---------------- HOSPITAL SIGNATURE MODE ----------------
    if hospital_mode:
        content.append(Paragraph(
            "<b><font color='blue'>Hospital Verified Certificate</font></b>",
            styles["Normal"]
        ))
        content.append(Spacer(1, 10))

    # ---------------- SIGNATURE ----------------
    content.append(Paragraph("<b>Authorized Medical Officer</b>", styles["Normal"]))
    content.append(Spacer(1, 10))

    if os.path.exists("signature.png"):
        content.append(Image("signature.png", width=120, height=50))

    content.append(Spacer(1, 10))
    content.append(Paragraph(data.get("hospital", "LifeLink Hospital"), styles["Normal"]))

    content.append(Spacer(1, 20))

    # ---------------- FOOTER ----------------
    content.append(Paragraph(
        "<font color='grey'>Digitally Generated • LifeLink Secure System</font>",
        styles["Italic"]
    ))

    doc.build(content)

    return filename, cert_id
