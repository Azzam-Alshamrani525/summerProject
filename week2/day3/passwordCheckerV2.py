import streamlit as st

def evaluate_password(password):
    """Returns (strength, reasons) without printing anything."""
    length_ok = len(password) >= 8
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_number = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)  # any non-alphanumeric char counts now

    checks = [length_ok, has_upper, has_lower, has_number, has_special]
    score = sum(checks)

    # Thresholds: 0-2 checks passed = Weak, 3-4 = Medium, all 5 = Strong
    WEAK_MAX = 2
    MEDIUM_MAX = 4

    if score <= WEAK_MAX:
        strength = "Weak"
    elif score <= MEDIUM_MAX:
        strength = "Medium"
    else:
        strength = "Strong"

    reasons = []
    if not length_ok:
        reasons.append("too short")
    if not has_upper:
        reasons.append("no uppercase letters")
    if not has_lower:
        reasons.append("no lowercase letters")
    if not has_number:
        reasons.append("no numbers")
    if not has_special:
        reasons.append("no special characters")

    return strength, reasons


st.title("Password Strength Checker")
password = st.text_input("Enter a password", type="password")

if password:
    strength, reasons = evaluate_password(password)
    st.subheader(strength)
    if reasons:
        st.write(", ".join(reasons).capitalize())
else:
    st.write("No password entered")