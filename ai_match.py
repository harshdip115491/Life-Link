import math


# =========================================
# BLOOD GROUP COMPATIBILITY
# =========================================

BLOOD_COMPATIBILITY = {
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"]
}


# =========================================
# CALCULATE URGENCY SCORE
# =========================================

def calculate_urgency_score(level):

    if not level:
        return 40

    level = str(level).lower()

    scores = {
        "critical": 100,
        "high": 80,
        "medium": 60,
        "low": 40
    }

    return scores.get(level, 40)


# =========================================
# WAITING TIME SCORE
# =========================================

def calculate_waiting_score(waiting_days):

    try:
        waiting_days = int(waiting_days)
    except:
        waiting_days = 0

    if waiting_days >= 365:
        return 100
    elif waiting_days >= 180:
        return 80
    elif waiting_days >= 90:
        return 60
    elif waiting_days >= 30:
        return 40

    return 20


# =========================================
# AGE COMPATIBILITY SCORE
# =========================================

def calculate_age_score(donor_age, patient_age):

    try:
        donor_age = int(donor_age)
        patient_age = int(patient_age)
    except:
        return 50

    difference = abs(donor_age - patient_age)

    if difference <= 5:
        return 100
    elif difference <= 10:
        return 80
    elif difference <= 20:
        return 60
    elif difference <= 30:
        return 40

    return 20


# =========================================
# DISTANCE SCORE
# =========================================

def calculate_distance_score(distance_km):

    try:
        distance_km = float(distance_km)
    except:
        distance_km = 50

    if distance_km <= 10:
        return 100
    elif distance_km <= 50:
        return 80
    elif distance_km <= 100:
        return 60
    elif distance_km <= 300:
        return 40

    return 20


# =========================================
# HOSPITAL SCORE
# =========================================

def calculate_hospital_score(success_rate, icu_available):

    try:
        success_rate = float(success_rate)
    except:
        success_rate = 70

    score = success_rate * 0.7

    if icu_available:
        score += 30

    return min(score, 100)


# =========================================
# SURVIVAL SCORE
# =========================================

def calculate_survival_score(age, severity):

    try:
        age = int(age)
    except:
        age = 40

    try:
        severity = int(severity)
    except:
        severity = 3

    score = 100

    score -= age * 0.3
    score -= severity * 5

    return max(score, 20)


# =========================================
# FINAL AI SCORE
# =========================================

def calculate_final_score(
    urgency_score,
    waiting_score,
    age_score,
    distance_score,
    hospital_score,
    survival_score
):

    final_score = (
        urgency_score * 0.30 +
        waiting_score * 0.20 +
        age_score * 0.15 +
        distance_score * 0.10 +
        hospital_score * 0.10 +
        survival_score * 0.15
    )

    return round(final_score, 2)


# =========================================
# MAIN AI MATCHING FUNCTION
# =========================================

def match_organ_advanced(db, donor):

    donor_blood = donor.get("blood", "")
    donor_organ = donor.get("organ", "")
    donor_age = donor.get("age", 30)

    cursor = db.conn.execute(
        """
        SELECT * FROM requests
        WHERE organ=?
        """,
        (donor_organ,)
    )

    requests = cursor.fetchall()

    matched_patients = []

    for patient in requests:

        try:
            patient_blood = patient["blood"]
        except:
            patient_blood = ""

        # =====================================
        # BLOOD GROUP COMPATIBILITY CHECK
        # =====================================

        compatible_groups = BLOOD_COMPATIBILITY.get(
            donor_blood,
            []
        )

        if patient_blood not in compatible_groups:
            continue

        # =====================================
        # SCORES
        # =====================================

        urgency_score = calculate_urgency_score(
            patient["urgency_level"]
            if "urgency_level" in patient.keys()
            else "medium"
        )

        waiting_score = calculate_waiting_score(
            patient["waiting_days"]
            if "waiting_days" in patient.keys()
            else 30
        )

        age_score = calculate_age_score(
            donor_age,
            patient["age"]
            if "age" in patient.keys()
            else 40
        )

        distance_score = calculate_distance_score(
            patient["distance_km"]
            if "distance_km" in patient.keys()
            else 50
        )

        hospital_score = calculate_hospital_score(
            patient["hospital_success_rate"]
            if "hospital_success_rate" in patient.keys()
            else 75,

            patient["icu_available"]
            if "icu_available" in patient.keys()
            else 1
        )

        survival_score = calculate_survival_score(
            patient["age"]
            if "age" in patient.keys()
            else 40,

            patient["disease_severity"]
            if "disease_severity" in patient.keys()
            else 3
        )

        # =====================================
        # FINAL SCORE
        # =====================================

        final_score = calculate_final_score(
            urgency_score,
            waiting_score,
            age_score,
            distance_score,
            hospital_score,
            survival_score
        )

        matched_patients.append({
            "patient_id": patient["id"]
            if "id" in patient.keys()
            else "",

            "patient_name": patient["patient_name"]
            if "patient_name" in patient.keys()
            else "Unknown",

            "hospital_name": patient["hospital_name"]
            if "hospital_name" in patient.keys()
            else "Unknown",

            "organ": donor_organ,
            "blood": patient_blood,

            "final_score": final_score,
            "urgency_score": urgency_score,
            "waiting_score": waiting_score,
            "survival_score": survival_score
        })

    # =========================================
    # SORT BEST PATIENT FIRST
    # =========================================

    matched_patients.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return matched_patients


# =========================================
# BACKWARD COMPATIBILITY
# OLD FUNCTION SUPPORT
# =========================================

def match_organ(db, organ, blood):

    donor = {
        "organ": organ,
        "blood": blood,
        "age": 30
    }

    return match_organ_advanced(db, donor)
