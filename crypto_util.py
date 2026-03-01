# simple_crypto_util.py
from cryptography.fernet import Fernet


# -------------------------------
# 生成金鑰 (只需做一次，之後存起來)
# -------------------------------
def generate_key():
    key = Fernet.generate_key()
    print(f"請把這個 key 存起來: {key.decode()}")
    return key

# -------------------------------
# 建立 Fernet 實例
# -------------------------------
def get_fernet(key: str):
    return Fernet(key.encode())

# -------------------------------
# 加密
# -------------------------------
def encrypt(text: str, key: str) -> str:
    f = get_fernet(key)
    encrypted = f.encrypt(text.encode())
    return encrypted.decode()

# -------------------------------
# 解密
# -------------------------------
def decrypt(encrypted_text: str, key: str) -> str:
    f = get_fernet(key)
    decrypted = f.decrypt(encrypted_text.encode())
    return decrypted.decode()


# -------------------------------
# 測試
# -------------------------------
if __name__ == "__main__":
    pass
    # 只需第一次生成
    # key = generate_key()
    # key = "TjxBjcM8dLfVI-zpFNJwD5WR5Zf5pxvMeUh37nhnuIk="  # 例: "hJd...==" 從 generate_key() 得到
    # message = "password"

    # encrypted = encrypt(message, key)
    # print("加密後:", encrypted)

    # decrypted = decrypt(encrypted, key)
    # print("解密後:", decrypted)
    
