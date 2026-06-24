# =========================================
# HOSPITAL PRIORITY AI
# BANK SIDE AI SYSTEM
# =========================================


# =========================================
# EMERGENCY SCORE
# =========================================

def calculate_emergency_score(emergency_cases):

    try:
        emergency_cases = int(emergency_cases)
    except:
        emergency_cases = 0

    score = emergency_cases * 20

    return min(score, 100)


# =========================================
# ICU SCORE
# =========================================

def calculate_icu_score(icu_available):

    if icu_available:
        return 100

    return 40


# =========================================
# SUCCESS RATE SCORE
# =========================================

def calculate_success_score(success_rate):

    try:
        success_rate = float(success_rate)
    except:
        success_rate = 70

    return min(success_rate, 100)


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
# SURGEON SCORE
# =========================================

def calculate_surgeon_score(surgeon_available):

    if surgeon_available:
        return 100

    return 50


# =========================================
# FINAL HOSPITAL SCORE
# =========================================

def calculate_final_hospital_score(
    emergency_score,
    icu_score,
    success_score,
    distance_score,
    surgeon_score
):

    final_score = (
        emergency_score * 0.30 +
        icu_score * 0.20 +
        success_score * 0.20 +
        distance_score * 0.15 +
        surgeon_score * 0.15
    )

    return round(final_score, 2)


# =========================================
# MAIN HOSPITAL PRIORITY AI
# =========================================

def prioritize_hospitals(db, organ):

    cursor = db.conn.execute(
        '''
        SELECT * FROM bank_requests
        WHERE organ_needed=?
        ''',
        (organ,)
    )

    hospitals = cursor.fetchall()

    ranked_hospitals = []

    for hospital in hospitals:

        emergency_score = calculate_emergency_score(
            hospital["emergency_cases"]
            if "emergency_cases" in hospital.keys()
            else 1
        )

        icu_score = calculate_icu_score(
            hospital["icu_available"]
            if "icu_available" in hospital.keys()
            else 1
        )

        success_score = calculate_success_score(
            hospital["success_rate"]
            if "success_rate" in hospital.keys()
            else 75
        )

        distance_score = calculate_distance_score(
            hospital["distance_km"]
            if "distance_km" in hospital.keys()
            else 50
        )

        surgeon_score = calculate_surgeon_score(
            hospital["surgeon_available"]
            if "surgeon_available" in hospital.keys()
            else 1
        )

        final_score = calculate_final_hospital_score(
            emergency_score,
            icu_score,
            success_score,
            distance_score,
            surgeon_score
        )

        ranked_hospitals.append({

            "hospital_name": hospital["hospital_name"]
            if "hospital_name" in hospital.keys()
            else "Unknown",

            "organ": organ,

            "final_score": final_score,

            "emergency_score": emergency_score,

            "icu_score": icu_score,

            "distance_score": distance_score,

            "success_score": success_score,

            "surgeon_score": surgeon_score
        })

    # =========================================
    # SORT BEST HOSPITAL FIRST
    # =========================================

    ranked_hospitals.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return ranked_hospitals
