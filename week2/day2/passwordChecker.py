def check_password(password):
    length_ok = len(password) >= 8
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_number = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    checks = [length_ok, has_upper, has_lower, has_number, has_special]
    score = sum(checks)

    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Medium"
    else:
        strength = "Strong"

    print(strength)

    if strength != "Strong":
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
        print(", ".join(reasons).capitalize())


print("Password Strength Checker — type 'end' to quit")

while True:
    password = input("\nEnter a password: ").strip()

    if password.lower() == "end":
        print("Goodbye!")
        break

    if password == "":
        print("No password entered")
        continue

    check_password(password)