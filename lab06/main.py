import sqlite3
from pathlib import Path

DB_NAME = "files_demo.db"

# 1) ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ (персональні дані + каталог файлів)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_username TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        is_private INTEGER NOT NULL
    )
    """)

    # щоб результати були стабільні — перезаписуємо тестові дані
    cur.execute("DELETE FROM users")
    cur.execute("DELETE FROM files")

    users = [
        ("administrator", "admin123", "Admin Root", "admin@demo.local"),
        ("olha", "qwerty", "Olha Khalina", "olha@demo.local"),
        ("ivan", "123456", "Ivan Petrenko", "ivan@demo.local"),
    ]
    cur.executemany(
        "INSERT INTO users (username, password, full_name, email) VALUES (?, ?, ?, ?)",
        users
    )

    files = [
        ("administrator", "server_keys.txt", "/etc/keys/server_keys.txt", 1),
        ("administrator", "audit_report.pdf", "/home/admin/audit_report.pdf", 1),
        ("olha", "course_notes.docx", "C:/Users/Olha/Documents/course_notes.docx", 0),
        ("olha", "passport_scan.jpg", "D:/Private/passport_scan.jpg", 1),
        ("ivan", "lab_results.xlsx", "C:/Users/Ivan/Desktop/lab_results.xlsx", 0),
    ]
    cur.executemany(
        "INSERT INTO files (owner_username, file_name, file_path, is_private) VALUES (?, ?, ?, ?)",
        files
    )

    conn.commit()
    conn.close()


# 2) ВРАЗЛИВИЙ ПОШУК (конкатенація рядка) — SQLi можлива
def vulnerable_file_search(conn, keyword: str):
    cur = conn.cursor()
    # ВРАЗЛИВО: користувацький ввід напряму підставляється в SQL
    query = f"""
    SELECT id, owner_username, file_name, file_path, is_private
    FROM files
    WHERE file_name LIKE '%{keyword}%'
    """
    print("\n[ВРАЗЛИВИЙ] SQL-запит:")
    print(query.strip())
    cur.execute(query)
    return cur.fetchall()


# 3) ЗАХИЩЕНИЙ ПОШУК
def safe_file_search(conn, keyword: str):
    cur = conn.cursor()
    # БЕЗПЕЧНО: параметризований запит
    query = """
    SELECT id, owner_username, file_name, file_path, is_private
    FROM files
    WHERE file_name LIKE ?
    """
    print("\n[ЗАХИЩЕНИЙ] SQL-запит:")
    print(query.strip())
    cur.execute(query, (f"%{keyword}%",))
    return cur.fetchall()


# 4) ДРУК РЕЗУЛЬТАТІВ
def print_files(rows):
    if not rows:
        print("Результат: [] (нічого не знайдено)")
        return
    print("Результат:")
    for r in rows:
        file_id, owner, name, path, is_private = r
        privacy = "PRIVATE" if is_private else "PUBLIC"
        print(f"  #{file_id} | {owner:<13} | {privacy:<7} | {name:<18} | {path}")


# 5) КОНСОЛЬНЕ МЕНЮ
def menu():
    conn = sqlite3.connect(DB_NAME)

    while True:
        print("\n==============================")
        print(" SQLi Demo: Каталог файлів")
        print("==============================")
        print("1) Вразливий пошук файлів (SQLi працює)")
        print("2) Захищений пошук файлів (SQLi блокується)")
        print("3) Підказка payload для атаки")
        print("0) Вихід")

        choice = input("Обери пункт: ").strip()

        if choice == "1":
            keyword = input("Введи ключове слово для пошуку (file_name): ").strip()
            try:
                rows = vulnerable_file_search(conn, keyword)
                print_files(rows)
            except sqlite3.Error as e:
                print(f"Помилка SQLite: {e}")

        elif choice == "2":
            keyword = input("Введи ключове слово для пошуку (file_name): ").strip()
            try:
                rows = safe_file_search(conn, keyword)
                print_files(rows)
            except sqlite3.Error as e:
                print(f"Помилка SQLite: {e}")

        elif choice == "3":
            print("\nСпробуй для вразливого пошуку (пункт 1) такий ввід:")
            print("  ' OR 1=1--")
            print("Очікування: у вразливому режимі поверне ВСІ файли, включно з PRIVATE.")

        elif choice == "0":
            break

        else:
            print("Невірний вибір. Спробуй ще раз.")

    conn.close()


if __name__ == "__main__":
    # створення БД та тестових даних
    init_db()
    print(f"Базу даних ініціалізовано: {Path(DB_NAME).resolve()}")
    menu()
