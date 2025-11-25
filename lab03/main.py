from PIL import Image
import os

# ЕТАП 1: ПОКРОКОВИЙ АЛГОРИТМ
"""
АЛГОРИТМ ПРИХОВУВАННЯ:
1. Конвертувати текст в байти, потім в біти
2. Додати спеціальний delimiter для визначення кінця повідомлення
3. Відкрити зображення та отримати доступ до пікселів
4. Для кожного біта повідомлення:
   - Взяти значення червоного каналу пікселя
   - Замінити молодший біт (LSB) на біт повідомлення
   - Зберегти модифікований піксель
5. Зберегти зображення в форматі PNG (без втрат)

АЛГОРИТМ ВИТЯГУВАННЯ:
1. Відкрити зображення з прихованим повідомленням
2. Читати молодші біти червоних каналів пікселів
3. Групувати біти в байти
4. Конвертувати байти в текст
5. Зупинитися при знаходженні delimiter
"""

# ЕТАП 2: РЕАЛІЗАЦІЯ ФУНКЦІЙ

def text_to_bits(text):
    bits = []
    for byte in text.encode("utf-8"):
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits


def bits_to_text(bits):
    ba = bytearray()
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            ba.append(byte)
    return ba.decode("utf-8", errors="ignore")

def hide_message(input_image_path, output_image_path, message):
    """
    Ховає повідомлення в зображення методом LSB
        input_image_path: шлях до вхідного зображення
        output_image_path: шлях для збереження зображення з повідомленням
        message: текст для приховування
    """
    # Додаємо delimiter для визначення кінця повідомлення
    delimiter = "###END###"
    full_message = message + delimiter
    
    # Конвертуємо повідомлення в біти
    message_bits = text_to_bits(full_message)
    
    # Відкриваємо зображення
    img = Image.open(input_image_path)
    img = img.convert('RGB')  # Конвертуємо в RGB якщо потрібно
    pixels = img.load()
    
    width, height = img.size
    max_bits = width * height * 3  # 3 канали RGB
    
    # Перевіряємо чи достатньо місця
    if len(message_bits) > max_bits:
        raise ValueError(f"Повідомлення завелике! Максимум {max_bits} біт, потрібно {len(message_bits)}")
    
    print(f"Зображення: {width}x{height} пікселів")
    print(f"Доступно біт: {max_bits}")
    print(f"Повідомлення: {len(message_bits)} біт ({len(full_message)} символів)")
    
    # Ховаємо повідомлення
    bit_index = 0
    for y in range(height):
        for x in range(width):
            if bit_index >= len(message_bits):
                break
                
            r, g, b = pixels[x, y]
            
            # Замінюємо LSB червоного каналу
            if bit_index < len(message_bits):
                r = (r & ~1) | message_bits[bit_index]
                bit_index += 1
            
            # Можна використовувати і зелений канал для більшої ємності
            if bit_index < len(message_bits):
                g = (g & ~1) | message_bits[bit_index]
                bit_index += 1
            
            # І синій канал
            if bit_index < len(message_bits):
                b = (b & ~1) | message_bits[bit_index]
                bit_index += 1
            
            pixels[x, y] = (r, g, b)
        
        if bit_index >= len(message_bits):
            break
    
    # Зберігаємо в PNG
    img.save(output_image_path, 'PNG')
    print(f"✓ Повідомлення заховано в {output_image_path}")


def extract_message(image_path):
    """
    Витягує приховане повідомлення з зображення
    image_path: шлях до зображення з прихованим повідомленням
    str: витягнуте повідомлення
    """
    delimiter = "###END###"
    
    # Відкриваємо зображення
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()
    
    width, height = img.size
    
    # Витягуємо біти
    bits = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            # Читаємо LSB з кожного каналу
            bits.append(r & 1)
            bits.append(g & 1)
            bits.append(b & 1)
    
    # Конвертуємо біти в текст
    text = bits_to_text(bits)
    
    # Шукаємо delimiter
    end_pos = text.find(delimiter)
    if end_pos != -1:
        return text[:end_pos]
    else:
        return text  # Якщо delimiter не знайдено, повертаємо весь текст


# ЕТАП 3: ДЕМОНСТРАЦІЯ НА ВЛАСНИХ ДАНИХ

def demo():
    # Створюємо тестове зображення якщо немає
    if not os.path.exists('original.png'):
        print("Створюю тестове зображення...")
        img = Image.new('RGB', (400, 300), color=(73, 109, 137))
        
        # Додаємо трохи шуму для реалістичності
        pixels = img.load()
        for y in range(300):
            for x in range(400):
                r, g, b = pixels[x, y]
                import random
                r = min(255, max(0, r + random.randint(-20, 20)))
                g = min(255, max(0, g + random.randint(-20, 20)))
                b = min(255, max(0, b + random.randint(-20, 20)))
                pixels[x, y] = (r, g, b)
        
        img.save('original.png', 'PNG')
        print("✓ Створено original.png")
    
    # Власні персональні дані для тесту
    secret_message = """Халіна Ольга Дмитріївна, 6.04.122.010.22.1, ДН: 10.05.2005"""
    
    print("ПРИХОВУВАННЯ ПОВІДОМЛЕННЯ")
    print(f"Оригінальне повідомлення:\n{secret_message}\n")
    
    # Ховаємо повідомлення
    hide_message('original.png', 'stego.png', secret_message)
    
    print("\nВИТЯГУВАННЯ ПОВІДОМЛЕННЯ")
    
    # Витягуємо повідомлення
    extracted = extract_message('stego.png')
    print(f"Витягнуте повідомлення:\n{extracted}\n")
    
    # Перевірка
    if extracted == secret_message:
        print("УСПІХ! Повідомлення витягнуто коректно!")
    else:
        print("ПОМИЛКА! Повідомлення відрізняється!")
    
    # ЕТАП 4: АНАЛІЗ ЗМІН
    print("\nАНАЛІЗ ЗМІН")
    
    original_size = os.path.getsize('original.png')
    stego_size = os.path.getsize('stego.png')
    
    print(f"Розмір оригіналу: {original_size} байт")
    print(f"Розмір стего: {stego_size} байт")
    print(f"Різниця: {stego_size - original_size} байт")
    
    # Порівняння пікселів
    img1 = Image.open('original.png')
    img2 = Image.open('stego.png')
    
    pixels1 = img1.load()
    pixels2 = img2.load()
    
    width, height = img1.size
    diff_count = 0
    max_diff = 0
    
    for y in range(height):
        for x in range(width):
            r1, g1, b1 = pixels1[x, y]
            r2, g2, b2 = pixels2[x, y]
            
            diff = abs(r1 - r2) + abs(g1 - g1) + abs(b1 - b2)
            if diff > 0:
                diff_count += 1
                max_diff = max(max_diff, diff)
    
    total_pixels = width * height
    print(f"\nВізуальні зміни:")
    print(f"Змінено пікселів: {diff_count} з {total_pixels}")
    print(f"Відсоток змін: {(diff_count/total_pixels)*100:.2f}%")
    print(f"Максимальна різниця: {max_diff} (зміна на 1 біт)")
    print("\nЗміни НЕПОМІТНІ для людського ока!")


# Запуск демонстрації
if __name__ == "__main__":
    demo()
