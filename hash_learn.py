"""
import hashlib
s='1'
m = hashlib.md5(s.encode())
print(m)
m = hashlib.sha224( s.encode() )
result = m.hexdigest()
print(result)

salt='24dfw32R@#@#@$'
password = input('password:')
password += salt
m = hashlib.md5( password.encode() )
result = m.hexdigest() #获取加密后的结果
print(result)


def md5(s,salt=''):
    new_s = str(s) + salt
    m = hashlib.md5(new_s.encode())
    return m.hexdigest()
"""

import base64
s='12345678'
b = base64.b64encode( s.encode() )
result= b.decode()
print(result)

b = base64.b64decode( '5ZOI5ZOI5ZOI5ZOI' )
print(b.decode())











