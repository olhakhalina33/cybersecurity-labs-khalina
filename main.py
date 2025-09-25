import re
import sys

DEFAULT_FULLNAME = "Khalina Olha Dmytriyivna"
DEFAULT_BIRTHDAY = "10.05.2005"

def split_name_parts(fullname: str):
    parts = re.split(r"\s+|-|_", fullname.strip())
    return [p.lower() for p in parts if p]

LEET_MAP = {'0': 'o','1': 'i','3': 'e','4': 'a','5': 's','7': 't','2': 'z','@': 'a','$': 's'}

def leet_normalize(s: str):
    return "".join(LEET_MAP.get(ch, ch) for ch in s.lower())

COMMON_WORDS = {"password", "qwerty", "admin", "user", "letmein", "welcome", "123456", "iloveyou"}

def analyze_password(password: str, fullname: str, birthday: str):
    pw = password.strip()
    lower_pw = pw.lower()
    score = 10.0
    deductions = []  # список: (причина, -бали)
    recommendations = []

    # --- Персональні дані ---
    name_parts = split_name_parts(fullname)
    for part in name_parts:
        if part and part in lower_pw:
            deductions.append((f"Знайдено ім'я/прізвище '{part}'", -3.0))
            recommendations.append("Не використовуйте ім'я або прізвище у паролі.")
    leet_pw = leet_normalize(pw)
    for part in name_parts:
        if part and part in leet_pw and part not in lower_pw:
            deductions.append((f"Знайдено leet-варіант імені '{part}'", -3.0))
            recommendations.append("Не використовуйте модифіковане ім'я у паролі.")

    bd_parts = re.findall(r"\d+", birthday)
    if len(bd_parts) >= 3:
        dd, mm, yyyy = bd_parts[0], bd_parts[1], bd_parts[2]
        bd_formats = {dd, mm, yyyy, yyyy[-2:], dd+mm, dd+mm+yyyy, mm+dd, birthday.replace(".", "")}
        for form in bd_formats:
            if form and form in lower_pw:
                deductions.append((f"Знайдено частину дати народження '{form}'", -3.0))
                recommendations.append("Не використовуйте дату народження у паролі.")

    # --- Довжина ---
    L = len(pw)
    if L < 8:
        deductions.append(("Довжина < 8 символів", -2.0))
        recommendations.append("Зробіть пароль хоча б 12 символів.")
    elif 8 <= L < 12:
        deductions.append(("Довжина 8–11 символів", -0.5))
        recommendations.append("Подовжіть пароль до 12+ символів.")
    else:
        score += 0.5

    # --- Різноманітність символів ---
    if not re.search(r"[A-ZА-ЯІЇЄҐ]", pw):
        deductions.append(("Відсутні великі літери", -0.8))
        recommendations.append("Додайте великі літери.")
    if not re.search(r"[a-zа-яіїєґ]", pw):
        deductions.append(("Відсутні маленькі літери", -0.8))
        recommendations.append("Додайте маленькі літери.")
    if not re.search(r"\d", pw):
        deductions.append(("Відсутні цифри", -0.8))
        recommendations.append("Додайте цифри.")
    if not re.search(r"[^A-Za-zА-Яа-яІЇЄҐіїєґ0-9]", pw):
        deductions.append(("Відсутні спеціальні символи", -1.0))
        recommendations.append("Додайте спецсимволи (!@#$%).")
    else:
        score += 0.2

    # --- Словникові слова ---
    found_common = [w for w in COMMON_WORDS if w in lower_pw]
    if found_common:
        deductions.append((f"Містить поширене слово: {', '.join(found_common)}", -2.0))
        recommendations.append("Уникайте простих словникових слів.")

    # --- Послідовності ---
    if re.search(r"(0123|1234|2345|3456|4567|5678|6789)", pw):
        deductions.append(("Містить цифрову послідовність (наприклад, 1234)", -1.0))
        recommendations.append("Не використовуйте послідовності цифр чи букв.")

    # --- Підрахунок фінальних балів ---
    for reason, penalty in deductions:
        score += penalty

    score = max(1.0, min(10.0, score))

    if score <= 3: level = "Дуже слабкий"
    elif score <= 5: level = "Слабкий"
    elif score <= 7: level = "Середній"
    elif score <= 9: level = "Сильний"
    else: level = "Надійний"

    return {
        "password": pw,
        "score": round(score, 1),
        "level": level,
        "deductions": deductions,
        "recommendations": list(dict.fromkeys(recommendations))
    }

def main():
    print("=== Password Auditor ===")
    fullname = input(f"Введіть повне ім'я [{DEFAULT_FULLNAME}]: ").strip() or DEFAULT_FULLNAME
    birthday = input(f"Введіть дату народження DD.MM.YYYY [{DEFAULT_BIRTHDAY}]: ").strip() or DEFAULT_BIRTHDAY

    print("\nВводьте паролі для перевірки (exit — вихід).\n")

    while True:
        pw = input("Пароль> ").strip()
        if pw.lower() in {"exit", "quit"}:
            print("Вихід.")
            break
        if not pw:
            print("Порожній ввід.\n")
            continue

        res = analyze_password(pw, fullname, birthday)
        print("\n--- Результат ---")
        print(f"Пароль: {res['password']}")
        print(f"Оцінка: {res['score']} / 10  ({res['level']})")
        if res['deductions']:
            print("Зняті бали:")
            for reason, penalty in res['deductions']:
                print(f" - {reason}: {penalty}")
        if res['recommendations']:
            print("Рекомендації:")
            for r in res['recommendations']:
                print(" -", r)
        print("------------------\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПерервано користувачем.")
        sys.exit(0)
