import string

from fastapi import FastAPI
from pydantic import BaseModel, Field


APP_VERSION = "0.1.0"

COMMON_PASSWORDS = {
    "123456", "12345678", "123456789", "1234567890",
    "password", "password1", "password123", "qwerty", "qwerty123",
    "admin", "admin123", "letmein", "iloveyou", "пароль",
}

CRITERIA = {
    "length": "Используйте не менее 12 символов.",
    "lowercase": "Добавьте строчную букву.",
    "uppercase": "Добавьте заглавную букву.",
    "digit": "Добавьте цифру.",
    "special": "Добавьте специальный символ из набора: " + string.punctuation,
    "no_repeats": "Избегайте трёх одинаковых символов подряд.",
    "no_sequences": "Избегайте последовательностей из четырёх символов, например 1234 или qwer.",
    "not_common": "Не используйте пароль из списка распространённых.",
}


class PasswordRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


app = FastAPI(
    title="Проверка паролей",
    description="Оценка паролей по заданным критериям и генерация случайных паролей.",
    version=APP_VERSION,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


@app.get("/criteria")
def criteria():
    return CRITERIA


@app.post("/check")
def check_password(data: PasswordRequest):
    password = data.password
    lowered = password.lower()
    sequences = ("0123456789", "abcdefghijklmnopqrstuvwxyz", "qwertyuiop", "asdfghjkl", "zxcvbnm")
    has_sequence = any(
        sequence[i:i + 4] in lowered or sequence[i:i + 4][::-1] in lowered
        for sequence in sequences
        for i in range(len(sequence) - 3)
    )
    has_repeat = any(
        lowered[i] == lowered[i + 1] == lowered[i + 2]
        for i in range(len(lowered) - 2)
    )

    checks = {
        "length": len(password) >= 12,
        "lowercase": any(char.islower() for char in password),
        "uppercase": any(char.isupper() for char in password),
        "digit": any(char.isdecimal() for char in password),
        "special": any(char in string.punctuation for char in password),
        "no_repeats": not has_repeat,
        "no_sequences": not has_sequence,
        "not_common": lowered not in COMMON_PASSWORDS,
    }
    score = sum(checks.values())
    if len(password) < 8 or not checks["not_common"] or score < 5:
        level = "weak"
    elif score == len(CRITERIA):
        level = "strong"
    else:
        level = "medium"

    return {
        "score": score,
        "max_score": len(CRITERIA),
        "level": level,
        "checks": checks,
        "recommendations": [CRITERIA[name] for name, passed in checks.items() if not passed],
    }
