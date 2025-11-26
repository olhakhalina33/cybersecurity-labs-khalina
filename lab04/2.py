import hashlib

def generate_keys(name: str, birth_date: str, secret_word: str):
    data = f"{name}|{birth_date}|{secret_word}"

    # "Приватний ключ"
    private_key = hashlib.sha256(data.encode("utf-8")).hexdigest()

    # "Публічний ключ" 
    priv_int = int(private_key, 16)
    public_int = priv_int * 7                   
    public_key = hex(public_int)[2:]           

    # Зберігаємо ключі в окремі файли
    with open("private_key.txt", "w", encoding="utf-8") as f:
        f.write(private_key)

    with open("public_key.txt", "w", encoding="utf-8") as f:
        f.write(public_key)

    return private_key, public_key


def main():
    name = input("Введіть ім'я та прізвище: ")
    birth_date = input("Введіть дату народження (наприклад, 10.05.2005): ")
    secret_word = input("Введіть секретне слово: ")

    private_key, public_key = generate_keys(name, birth_date, secret_word)

    print("\nКлючі згенеровано!")
    print("Приватний ключ (хеш):")
    print(private_key)
    print("\nПублічний ключ (пов'язана величина):")
    print(public_key)
    print("\nКлючі збережено у файли 'private_key.txt' та 'public_key.txt'.")

if __name__ == "__main__":
    main()
