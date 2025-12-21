import time
import hashlib
from cryptography.fernet import Fernet
from PIL import Image

# ================== Персональні дані ==================
FULL_NAME = "Халіна Ольга Дмитріївна"
BIRTHDATE = "10.05.2005"

# ================== AES ключ ==================
def generate_key():
    data = (FULL_NAME + BIRTHDATE).encode()
    return hashlib.sha256(data).digest()[:32]

def get_fernet():
    return Fernet(Fernet.generate_key())

# ================== AES ==================
def encrypt_file(path, fernet):
    with open(path, "rb") as f:
        return fernet.encrypt(f.read())

def decrypt_file(data, fernet):
    return fernet.decrypt(data)

# ================== LSB ==================
def hide_data(image_path, data, out_path):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    size = len(data)
    header = size.to_bytes(4, "big")   # 4 байти довжини
    data = header + data

    bits = ''.join(f"{b:08b}" for b in data)
    new_pixels = []
    i = 0

    for r, g, b in pixels:
        if i < len(bits): r = (r & ~1) | int(bits[i]); i += 1
        if i < len(bits): g = (g & ~1) | int(bits[i]); i += 1
        if i < len(bits): b = (b & ~1) | int(bits[i]); i += 1
        new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    img.save(out_path)

def extract_data(image_path):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    bits = []
    for r, g, b in pixels:
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))

    size = int(''.join(bits[:32]), 2)  # перші 32 біти - розмір
    data_bits = bits[32:32 + size * 8]

    data = bytearray()
    for i in range(0, len(data_bits), 8):
        data.append(int(''.join(data_bits[i:i+8]), 2))

    return bytes(data)

# ================== MAIN ==================
def main():
    print("=== Комплексна система захисту (AES + LSB) ===")

    file_path = input("Файл для захисту: ")
    image_path = input("Зображення: ")

    fernet = get_fernet()

    # ---------- Захист ----------
    t1 = time.time()
    encrypted = encrypt_file(file_path, fernet)
    t2 = time.time()

    hide_data(image_path, encrypted, "protected.png")
    t3 = time.time()

    print("\n--- Етап захисту ---")
    print(f"Час AES: {t2 - t1:.4f} с")
    print(f"Час LSB: {t3 - t2:.4f} с")
    print("Файл захищено у protected.png")

    # ---------- Відновлення ----------
    print("\n--- Відновлення ---")
    hidden = extract_data("protected.png")

    print("Спроба читання без дешифрування:")
    print(hidden[:20], "(нечитабельно)")

    restored = decrypt_file(hidden, fernet)
    with open("restored.txt", "wb") as f:
        f.write(restored)

    t4 = time.time()
    print(f"Час відновлення: {t4 - t3:.4f} с")
    print("Файл відновлено: restored.txt")

if __name__ == "__main__":
    main()
