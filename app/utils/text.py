import re


def to_correct_message(text: str) -> str:
    return (
        text.replace("+", "\\+")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("-", "\\-")
        .replace("_", "\\_")
    )


def convert_text_to_phone(phone: str) -> str:
    phone = phone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")

    if phone.startswith("8"):
        phone = phone.replace("8", "+7", 1)
    elif phone.startswith("7"):
        phone = phone.replace("7", "+7", 1)
    return phone


def is_correct_phone(phone: str) -> bool:
    phone = phone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")

    if phone.startswith("8"):
        phone = phone.replace("8", "+7", 1)
    elif phone.startswith("7"):
        phone = phone.replace("7", "+7", 1)

    if re.match(r"\+7\d{10}$", phone):
        return True
    return False


def format_phone(phone: str) -> str:
    phone_pattern = re.compile(r"(\+7)(\d{3})(\d{3})(\d{2})(\d{2})")
    format_pattern = r"\1 (\2) \3-\4-\5"
    formatted_phone = re.sub(phone_pattern, format_pattern, phone)
    return formatted_phone
