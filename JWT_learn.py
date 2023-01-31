from datetime import timedelta, datetime
import jwt
from fastapi import FastAPI, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request

app = FastAPI()

SECRET_KEY = "sdifhgsiasfjaofhslio"  # JWY签名所使用的密钥，是私密的，只在服务端保存
ALGORITHM = "HS256"  # 加密算法，我这里使用的是HS256


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/create_token")
def create_token(username, password):
    if username == "123" and password == "123":
        access_token_expires = timedelta(minutes=60)
        expire = datetime.utcnow() + access_token_expires

        payload = {
            "sub": username,
            "exp": expire
        }
        # 生成Token,返回给前端
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": access_token, "token_type": "bearer"}

    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="username or password are not true",
            headers={"WWW-Authenticate": "Bearer"}
        )


def authorized_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(username)
        if username == "123":
            return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败,无权查看",
            headers={"WWW-Authenticate": "Bearer"}, )


@app.get("/app")
def create_token(request: Request):
    print(request.headers.get("host"), request.headers.get("Authorization"))
    user = authorized_user(request.headers.get("Authorization"))  # 验证Token
    if user:
        return {"username": user, "detail": "JWT通过，查询成功"}