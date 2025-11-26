import hashlib
import os

class DigitalSignatureSystem:
    def __init__(self):
        self.MODULUS = 1000007
        self.PUBLIC_MULTIPLIER = 7
        self.private_key = None
        self.public_key = None
        
    def generate_keys(self, surname, birthdate, secret_word):
        """Генерація пари ключів на основі персональних даних"""
        combined = f"{surname}{birthdate}{secret_word}"
        hash_obj = hashlib.sha256(combined.encode())
        self.private_key = int(hash_obj.hexdigest(), 16) % self.MODULUS
        self.public_key = (self.private_key * self.PUBLIC_MULTIPLIER) % self.MODULUS
        
        print(f"\n✓ Ключі згенеровано:")
        print(f"  Приватний ключ: {self.private_key}")
        print(f"  Публічний ключ: {self.public_key}")
        
    def hash_document(self, content):
        """Обчислення хешу документу"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def sign_document(self, content):
        """Створення цифрового підпису"""
        if not self.private_key:
            raise ValueError("Спочатку згенеруйте ключі!")
        
        doc_hash = self.hash_document(content)
        hash_int = int(doc_hash, 16)
        signature = hash_int ^ self.private_key
        
        print(f"\n✓ Документ підписано")
        print(f"  Хеш документу: {doc_hash[:32]}...")
        print(f"  Підпис: {signature}")
        
        return signature, doc_hash
    
    def verify_signature(self, content, signature, original_hash):
        """Перевірка цифрового підпису"""
        if not self.public_key:
            raise ValueError("Публічний ключ відсутній!")
        
        current_hash = self.hash_document(content)
        decrypted = signature ^ self.private_key
        expected_hash_int = int(original_hash, 16)
        
        print(f"\n--- Перевірка підпису ---")
        print(f"Оригінальний хеш: {original_hash[:32]}...")
        print(f"Поточний хеш:     {current_hash[:32]}...")
        
        if current_hash == original_hash and decrypted == expected_hash_int:
            print("✓ Результат: Підпис ДІЙСНИЙ ✓")
            return True
        else:
            print("✗ Результат: Підпис ПІДРОБЛЕНИЙ ✗")
            return False

def main():
    system = DigitalSignatureSystem()
    
    print("СИСТЕМА ЦИФРОВИХ ПІДПИСІВ")
    
    # Генерація ключів
    print("\n[1] Генерація ключів")
    surname = input("Введіть прізвище: ")
    birthdate = input("Введіть дату народження (DDMMYYYY): ")
    secret = input("Введіть секретне слово: ")
    
    system.generate_keys(surname, birthdate, secret)
    
    # Створення та підпис документу
    print("\n[2] Створення документу")
    document = input("Введіть текст документу: ")
    
    signature, doc_hash = system.sign_document(document)
    
    # Перевірка дійсного підпису
    print("\n[3] Перевірка оригінального документу")
    system.verify_signature(document, signature, doc_hash)
    
    # Демонстрація підробки
    print("\n[4] Демонстрація підробки")
    choice = input("Змінити документ? (y/n): ")
    
    if choice.lower() == 'y':
        fake_document = input("Введіть змінений текст: ")
        system.verify_signature(fake_document, signature, doc_hash)

if __name__ == "__main__":
    main()
