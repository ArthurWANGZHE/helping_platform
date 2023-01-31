from datetime import datetime, timedelta

import jwt
from jwt import ExpiredSignatureError

# 加密密钥 这个很重要千万不能泄露了
SECRET_KEY = "kkkkk"

# 设置过期时间 现在时间 + 有效时间    示例5分钟
expire = datetime.utcnow() + timedelta(minutes=5)

# exp 是固定写法必须得传  sub和uid是自己存的值
to_encode = {"exp": expire, "sub": str(123), "uid": "12345"}

# 生成token
encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
print(encoded_jwt)
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTU1MDg5MzQsInN1YiI6IjEyMyIsInVpZCI6IjEyMzQ1In0.lttAYe808lVQgGhL9NXei2bbC1LIGs-SS0l6qfU_QxU


payload = jwt.decode(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzUxNjM0MDUsInN1YiI6IjEyMyIsInVpZCI6IjEyMzQ1In0.jMdPaTmYVa_mx9W18oAyi7wLepUpeHAmpzXUahxoCxw",
            SECRET_KEY, algorithms="HS256"
        )
print(payload)

# {'exp': 1595508934, 'sub': '123', 'uid': '12345'}
class JWTError:
    pass


try:
    payload = jwt.decode(
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTU1MDk0ODQsInN1YiI6IjEyMyIsInVpZCI6IjEyMzQ1In0.deulPSOPfON-lfbXtvQfTfc-DwqvFoQqv7Y1BhMecBw",
                SECRET_KEY, algorithms="HS256"
            )
    print(payload)
# 当然两个异常捕获也可以写在一起，不区分
except ExpiredSignatureError as e:
    print("token过期")
except JWTError as e:
    print("token验证失败")

######################################################################################
from datetime import datetime, timedelta
from typing import Any, Union, Optional
import jwt
from fastapi import Header
# 导入配置文件
from setting import config

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    # 生成token
    :param subject: 保存到token的值
    :param expires_delta: 过期时间
    :return:
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_jwt_token(
     token: Optional[str] = Header(...)
) -> Union[str, Any]:
    """
    解析验证 headers中为token的值 当然也可以用 Header(..., alias="Authentication") 或者 alias="X-token"
    :param token:
    :return:
    """

    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except (jwt.JWTError, jwt.ExpiredSignatureError, AttributeError):
        # 抛出自定义异常， 然后捕获统一响应
        raise custom_exc.TokenAuthError(err_desc="access token fail")
