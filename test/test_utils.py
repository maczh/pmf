import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.base64util import base64_encode, base64_decode
from utils.desutil import *

if __name__ == "__main__":
    original = "Hello, World!"
    encoded = base64_encode(original)
    print(encoded)
    decoded = base64_decode(encoded)
    print(decoded)
    crypted = des_encrypt_str(original, "12345678")
    print(crypted)
    decrypted = des_decrypt_str(crypted, "12345678")
    print(decrypted)