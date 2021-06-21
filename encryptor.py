from cryptography.fernet import Fernet

# If you want to make your own secret key, use this as a reference
# https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/
SEC_KEY="SEC_KEY_HERE"

def main():
    text_to_encrypt = input("Text to Encrypt: ")
    encrypted_text = encrypt_text(text_to_encrypt)
    print("Encrypted form: " + encrypted_text)
    print("Decrypted Check: " + decrypt_text(encrypted_text))
    
def encrypt_text(text):
    f = Fernet(SEC_KEY)
    return f.encrypt(text.encode()).decode()
    
def decrypt_text(text):
    f = Fernet(SEC_KEY)
    return f.decrypt(text.encode()).decode()

if __name__ == '__main__':
    main()