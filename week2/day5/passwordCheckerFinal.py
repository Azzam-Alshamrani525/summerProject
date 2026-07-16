import streamlit as st

COMMON_PASSWORDS = {"password", "12345678", "qwertyui", "letmein1", "password1", "password1!"}

def evaluate_password(password):
    """Returns (strength, reasons) without printing anything."""
    length_ok = len(password) >= 8
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_number = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    is_common = password.lower() in COMMON_PASSWORDS
    not_common = not is_common

    checks = [length_ok, has_upper, has_lower, has_number, has_special, not_common]
    score = sum(checks)  # out of 6

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    elif score == 5:
        strength = "Medium-High"
    else:
        strength = "Strong"

    reasons = []
    if is_common:
        reasons.append("this is a commonly used password")
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
st.caption("Checks: length (8+), uppercase, lowercase, number, special character, not a common password")

password = st.text_input("Enter a password", type="password")

if password:
    strength, reasons = evaluate_password(password)
    st.subheader(strength)
    if reasons:
        st.write(", ".join(reasons).capitalize())
else:
    st.write("No password entered")