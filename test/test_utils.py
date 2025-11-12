import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.base64util import base64_encode, base64_decode
from utils.desutil import *
from utils.aesutil import *

if __name__ == "__main__":
    original = "Hello, World!"
    # encoded = base64_encode(original)
    # print(encoded)
    # decoded = base64_decode(encoded)
    # print(decoded)
    crypted = aes_encrypt_base64(original.encode(), b'1234567890123456',iv=b'1234567890123456', mode="CBC", padding="pkcs5")
    print(crypted)
    decrypted = aes_decrypt_base64(crypted, b"1234567890123456",iv=b'1234567890123456',mode="CBC", padding="pkcs5")
    print(decrypted.decode())