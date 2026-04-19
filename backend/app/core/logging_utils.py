def mask_email(email: str) -> str:
    local, sep, domain = email.partition("@")
    if not sep:
        return "***"

    if len(local) <= 1:
        masked_local = "*"
    elif len(local) == 2:
        masked_local = f"{local[0]}*"
    else:
        masked_local = f"{local[:2]}{'*' * (len(local) - 2)}"

    return f"{masked_local}@{domain}"
