import base64
from dataclasses import dataclass
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# =====================================
# Генерація ключа з персональних даних
# =====================================

def derive_key_from_personal_data(email: str, personal_string: str) -> bytes:
    """
    Генерує симетричний ключ на основі персональних даних користувача.
    - email використовується як 'salt'
    - personal_string – секретна фраза/пароль (наприклад, 'OlhaKhalina2005')
    """
    salt = email.encode("utf-8")
    personal_bytes = personal_string.encode("utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,           # 256-бітний ключ
        salt=salt,
        iterations=390000,   # кількість ітерацій для захисту від перебору
    )

    raw_key = kdf.derive(personal_bytes)
    fernet_key = base64.urlsafe_b64encode(raw_key)
    return fernet_key


def create_fernet_from_user_data(email: str, personal_string: str) -> Fernet:
    key = derive_key_from_personal_data(email, personal_string)
    return Fernet(key)


# ===========================================
# Модель "листа" (електронного повідомлення)
# ===========================================

@dataclass
class EncryptedEmail:
    from_email: str
    to_email: str
    subject: str
    encrypted_body: str            # зашифрований текст повідомлення (base64-рядок)
    encrypted_attachment: Optional[bytes] = None  # опційно: зашифрований файл (якщо є)


# ===================================
# Функції шифрування / розшифрування
# ===================================

def encrypt_message(email: str, personal_string: str, plaintext: str) -> str:
    """
    Шифрує текст повідомлення, повертає base64-рядок (token Fernet).
    """
    f = create_fernet_from_user_data(email, personal_string)
    token = f.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_message(email: str, personal_string: str, encrypted_text: str) -> str:
    """
    Розшифровує base64-рядок, повертає звичайний текст.
    """
    f = create_fernet_from_user_data(email, personal_string)
    decrypted_bytes = f.decrypt(encrypted_text.encode("utf-8"))
    return decrypted_bytes.decode("utf-8")


def encrypt_file(email: str, personal_string: str, file_path: str) -> bytes:
    """
    Просте шифрування файлового вкладення. Повертає зашифровані байти.
    """
    f = create_fernet_from_user_data(email, personal_string)
    with open(file_path, "rb") as f_in:
        data = f_in.read()
    token = f.encrypt(data)
    return token


def decrypt_file(email: str, personal_string: str, encrypted_data: bytes, output_path: str) -> None:
    """
    Розшифровує зашифровані байти файлу і зберігає у output_path.
    """
    f = create_fernet_from_user_data(email, personal_string)
    decrypted = f.decrypt(encrypted_data)
    with open(output_path, "wb") as f_out:
        f_out.write(decrypted)


# =======================================
# Демонстрація процесу безпечного обміну
# =======================================

def demo_exchange():
    print("=== Демонстрація безпечного обміну повідомленнями ===\n")

    # Дані користувача 
    user_email = "olgakhalina3@gmail.com"
    personal_string = "OlhaKhalina2005"  # персональні дані -> 'ключ' / пароль

    message = "Зустрічаємося завтра о 15:00"

    print(f"Електронна адреса відправника: {user_email}")
    print(f"Персональний рядок (для генерації ключа): {personal_string}")
    print(f"Оригінальне повідомлення: {message}\n")

    # === ВІДПРАВНИК ШИФРУЄ ===
    encrypted = encrypt_message(user_email, personal_string, message)
    print("Відправник шифрує повідомлення...")
    print(f"Зашифровані дані (token):\n{encrypted}\n")

    # === ОДЕРЖУВАЧ РОЗШИФРОВУЄ ===
    print("Одержувач отримує зашифрований текст і володіє тими ж персональними даними.")
    decrypted = decrypt_message(user_email, personal_string, encrypted)
    print(f"Розшифроване повідомлення: {decrypted}\n")

    # Перевірка
    if decrypted == message:
        print("Повідомлення успішно розшифроване. Обмін вважається коректним.")
    else:
        print("Щось пішло не так: текст після розшифрування не співпадає.")


# ===============
# Консольне меню 
# ===============

def main_menu():
    while True:
        print("\n=== Email-шифратор ===")
        print("1. Зашифрувати повідомлення")
        print("2. Розшифрувати повідомлення")
        print("3. Демонстрація обміну (готовий приклад)")
        print("4. Вихід")
        choice = input("Оберіть пункт меню: ").strip()

        if choice == "1":
            email = input("Введіть email (буде використано як сіль): ").strip()
            personal = input("Введіть персональний рядок (пароль/фраза): ").strip()
            text = input("Введіть текст повідомлення: ").strip()
            encrypted = encrypt_message(email, personal, text)
            print("\n=== Результат шифрування ===")
            print(encrypted)
            print("Скопіюйте цей рядок та надішліть одержувачу.\n")

        elif choice == "2":
            email = input("Введіть email (такий самий, як у відправника): ").strip()
            personal = input("Введіть персональний рядок (той самий, що у відправника): ").strip()
            enc_text = input("Вставте зашифрований текст: ").strip()
            try:
                decrypted = decrypt_message(email, personal, enc_text)
                print("\n=== Розшифрований текст ===")
                print(decrypted)
            except Exception as e:
                print(f"\nПомилка розшифрування: {e}")

        elif choice == "3":
            demo_exchange()

        elif choice == "4":
            print("Вихід...")
            break

        else:
            print("Невірний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main_menu()
