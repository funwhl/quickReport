import base64

from pyDes import des, CBC, PAD_PKCS5


class cyUtils:
    def __init__(self):
        self.Des_Key = "qwerty"  # Key
        self.Des_IV = "asdfg"  # 自定IV向量

    # 使用DES加base64的形式加密
    def encrypt(self, s):
        k = des(self.Des_Key, CBC, self.Des_IV, pad=None, padmode=PAD_PKCS5)
        return base64.b64encode(k.encrypt(s)).decode()

    # des解码
    def decrypt(self, s):
        s = base64.b64decode(s)
        k = des(self.Des_Key, CBC, self.Des_IV, pad=None, padmode=PAD_PKCS5)
        return k.decrypt(s, padmode=PAD_PKCS5).decode()
