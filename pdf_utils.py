import os
import uuid
import qrcode

from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ==========================================
# ORGAN FORMAT
# ==========================================

def format_organ(organ):

    if isinstance(organ, list):
        organ = ", ".join(organ)

    organ = str(organ).lower()

    if "heart" in organ:
        return "Heart"

    elif "kidney" in organ:
        return "Kidney"

    elif "liver" in organ:
        return "Liver"

    elif "eye" in organ:
        return "Eye"

    elif "multiple" in organ:
        return "Multiple Organs"

    return organ.title()


# ==========================================
# CERTIFICATE ID
# ==========================================

def generate_cert_id():

    return (
        "LL-"
        + datetime.now().strftime("%Y%m%d")
        + "-"
        + str(uuid.uuid4())[:6].upper()
    )


# ==========================================
# VERIFICATION URL
# ==========================================

def build_verification_url(cert_id):

    return f"https://lifelink.verify/certificate/{cert_id}"


# ==========================================
# MAIN PDF GENERATOR
# ==========================================

def generate_certificate_production(
    data,
    username,
    organ,
    hospital_mode=False
):

    os.makedirs("certificates", exist_ok=True)
    os.makedirs("certificates/qr", exist_ok=True)

    cert_id = generate_cert_id()

    filename = f"certificates/{cert_id}.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    content = []

    # ======================================
    # HEADER
    # ======================================

    if hospital_mode:

        title = """
        <b>
        <font size='20' color='darkred'>
        LIFE+LINK OFFICIAL DEATH CERTIFICATE
        </font>
        </b>
        """

    else:

        title = """
        <b>
        <font size='20' color='darkgreen'>
        LIFE+LINK ORGAN DONATION REGISTRATION CERTIFICATE
        </font>
        </b>
        """

    content.append(
        Paragraph(
            title,
            styles["Title"]
        )
    )

    content.append(Spacer(1, 15))

    # ======================================
    # CERTIFICATE INFO
    # ======================================

    content.append(
        Paragraph(
            f"<b>Certificate ID:</b> {cert_id}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Generated On:</b> "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 20))

    # ======================================
    # HOSPITAL DEATH CERTIFICATE
    # ======================================

    if hospital_mode:

        content.append(
            Paragraph(
                f"<b>Patient Name:</b> "
                f"{data.get('name', 'N/A')}",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Hospital Name:</b> "
                f"{data.get('hospital', 'N/A')}",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Cause Of Death:</b> "
                f"{data.get('cause', 'N/A')}",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Date & Time Of Death:</b> "
                f"{data.get('date', 'N/A')}",
                styles["Normal"]
            )
        )
   
        content.append(
            Paragraph(
                "<b>Organ Recovery Status:</b> "
                "Approved For Donation",
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 20))

        content.append(
            Paragraph(
                """
                <font color='red'>
                <b>
                Certified Cause Of Death Verified
                By Hospital Authority
                </b>
                </font>
                """,
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 20))

    # ======================================
    # USER ORGAN REGISTRATION
    # ======================================

    else:

        content.append(
            Paragraph(
                f"<b>Name:</b> "
                f"{data.get('name', 'N/A')}",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Username:</b> "
                f"{username}",
                styles["Normal"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Organ Registered:</b> "
                f"{format_organ(organ)}",
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 20))

    # ======================================
    # QR CODE
    # ======================================

    verify_url = build_verification_url(cert_id)

    qr = qrcode.make(verify_url)

    qr_path = f"certificates/qr/{cert_id}.png"

    qr.save(qr_path)

    content.append(
        Paragraph(
            "<b>Scan QR For Verification</b>",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 5))

    content.append(
        Image(
            qr_path,
            width=120,
            height=120
        )
    )

    content.append(Spacer(1, 20))

    # ======================================
    # SIGNATURE
    # ======================================

    content.append(
        Paragraph(
            "<b>Authorized Medical Officer</b>",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 10))

    if os.path.exists("signature.png"):

        content.append(
            Image(
                "signature.png",
                width=120,
                height=50
            )
        )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            data.get(
                "hospital",
                "Life+Link Network"
            ),
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 20))

    # ======================================
    # FOOTER
    # ======================================

    content.append(
        Paragraph(
            """
            <font color='grey'>
            Digitally Generated •
            Life+Link Organ Donation &
            Transplant Management System
            </font>
            """,
            styles["Italic"]
        )
    )

    doc.build(content)

    return filename, cert_id