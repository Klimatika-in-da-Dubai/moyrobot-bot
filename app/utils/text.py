SPECIAL_CHARS = [
    "\\",
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "<",
    "&",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
]


def escape_chars(text: str | None) -> str:
    if text is None:
        return ""
    for char in SPECIAL_CHARS:
        text = text.replace(char, "\\" + char)
    return text
