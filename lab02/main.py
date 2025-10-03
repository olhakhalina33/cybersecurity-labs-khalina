import math
from collections import Counter

class CaesarCipher:
    def __init__(self, shift):
        # Алфавіт української мови
        self.alphabet = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
        self.shift = shift % len(self.alphabet)

    def encrypt(self, msg):
        out_text = []
        for ch in msg.lower():
            if ch in self.alphabet:
                idx = self.alphabet.index(ch)
                new_idx = (idx + self.shift) % len(self.alphabet)
                out_text.append(self.alphabet[new_idx])
            else:
                out_text.append(ch)
        return ''.join(out_text)

    def decrypt(self, msg):
        out_text = []
        for ch in msg.lower():
            if ch in self.alphabet:
                idx = self.alphabet.index(ch)
                new_idx = (idx - self.shift) % len(self.alphabet)
                out_text.append(self.alphabet[new_idx])
            else:
                out_text.append(ch)
        return ''.join(out_text)


class AffineCipher:
    def __init__(self, a, b):
        self.alphabet = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
        self.m = len(self.alphabet)
        # Якщо a не взаємно просте з m, беремо інше
        if math.gcd(a, self.m) != 1:
            a = self._fix_a(a)
        self.a = a
        self.b = b % self.m

    def _fix_a(self, a):
        for i in range(a, a + 20):
            if math.gcd(i, self.m) == 1:
                return i
        return 5

    def _inverse(self, a, m):
        for i in range(1, m):
            if (a * i) % m == 1:
                return i
        return 1

    def encrypt(self, msg):
        out_text = []
        for ch in msg.lower():
            if ch in self.alphabet:
                idx = self.alphabet.index(ch)
                new_idx = (self.a * idx + self.b) % self.m
                out_text.append(self.alphabet[new_idx])
            else:
                out_text.append(ch)
        return ''.join(out_text)

    def decrypt(self, msg):
        out_text = []
        a_inv = self._inverse(self.a, self.m)
        for ch in msg.lower():
            if ch in self.alphabet:
                idx = self.alphabet.index(ch)
                new_idx = (a_inv * (idx - self.b)) % self.m
                out_text.append(self.alphabet[new_idx])
            else:
                out_text.append(ch)
        return ''.join(out_text)


def make_keys(date, surname):
    # Цезар: зсув = сума цифр дати
    shift = sum(int(x) for x in date if x.isdigit())
    # Афінний: a = сума кодів букв прізвища, b = довжина прізвища
    a = sum(ord(ch) for ch in surname.lower())
    b = len(surname)
    return shift, a, b


def quick_analysis(original, encrypted):
    alphabet = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
    changed = sum(1 for i in range(len(original)) if original[i] != encrypted[i])
    freq = Counter(ch for ch in encrypted.lower() if ch in alphabet)
    return {
        'довжина': len(encrypted),
        'змінено': changed,
        'найчастіші': freq.most_common(3)
    }


def menu_encrypt(caesar, affine):
    print("\n--- Шифрування ---")
    msg = input("Введіть текст: ")
    print("1. Цезар")
    print("2. Афінний")
    print("3. Обидва")
    choice = input("Ваш вибір: ")
    if choice == '1':
        print("Результат (Цезар):", caesar.encrypt(msg))
    elif choice == '2':
        print("Результат (Афінний):", affine.encrypt(msg))
    elif choice == '3':
        print("Цезар:", caesar.encrypt(msg))
        print("Афінний:", affine.encrypt(msg))


def menu_decrypt(caesar, affine):
    print("\n--- Розшифрування ---")
    msg = input("Введіть зашифрований текст: ")
    print("1. Цезар")
    print("2. Афінний")
    choice = input("Ваш вибір: ")
    if choice == '1':
        print("Розшифровано:", caesar.decrypt(msg))
    elif choice == '2':
        print("Розшифровано:", affine.decrypt(msg))


def menu_compare(caesar, affine):
    print("\n--- Порівняння ---")
    msg = input("Введіть текст: ")
    c_enc = caesar.encrypt(msg)
    a_enc = affine.encrypt(msg)
    print("Оригінал:", msg)
    print("Цезар:", c_enc)
    print("Афінний:", a_enc)
    c_stat = quick_analysis(msg, c_enc)
    a_stat = quick_analysis(msg, a_enc)
    print("\nТаблиця:")
    print(f"{'Параметр':<20} {'Цезар':<15} {'Афінний':<15}")
    print(f"{'Довжина':<20} {c_stat['довжина']:<15} {a_stat['довжина']:<15}")
    print(f"{'Змінено':<20} {c_stat['змінено']:<15} {a_stat['змінено']:<15}")
    print(f"{'Складність ключа':<20} {'Низька':<15} {'Середня':<15}")
    print("\nВисновок:")
    print("Цезар має лише 33 ключі, Афінний стійкіший, але обидва слабкі для сучасних задач.")


def main():
    date = input("Введіть дату народження (наприклад, 15.03.2000): ")
    surname = input("Введіть прізвище (наприклад, Халіна): ")
    c_shift, a_a, a_b = make_keys(date, surname)
    print("Згенеровані ключі:")
    print("Цезар:", c_shift)
    print("Афінний: a=", a_a, ", b=", a_b)
    caesar = CaesarCipher(c_shift)
    affine = AffineCipher(a_a, a_b)
    while True:
        print("\nМеню:")
        print("1. Шифрувати")
        print("2. Дешифрувати")
        print("3. Порівняти")
        print("4. Нові ключі")
        print("0. Вихід")
        choice = input("Ваш вибір: ")
        if choice == '1':
            menu_encrypt(caesar, affine)
        elif choice == '2':
            menu_decrypt(caesar, affine)
        elif choice == '3':
            menu_compare(caesar, affine)
        elif choice == '4':
            date = input("Нова дата: ")
            surname = input("Нове прізвище: ")
            c_shift, a_a, a_b = make_keys(date, surname)
            caesar = CaesarCipher(c_shift)
            affine = AffineCipher(a_a, a_b)
            print("Ключі оновлено")
        elif choice == '0':
            print("Вихід")
            break
        else:
            print("Невірний вибір")


if __name__ == "__main__":
    main()
