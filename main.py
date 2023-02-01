import uvicorn
from fastapi import FastAPI,UploadFile,File,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt
import base64
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request


Base = declarative_base()
engine = create_engine('mysql://root:123456@127.0.0.1:3306/db', echo=True)

class User(Base):
    __tablename__ = 'user'
    name = Column(String(20),primary_key=True)
    password = Column(String(20))
    bonus_points = Column(Integer)
class Project(Base):
    __tablename__ = 'project'
    name = Column(String(20), primary_key=True)
    bonus_points= Column(String(20))
    describe = Column(String(20))
    picture = Column(String(20))

Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
DBSession = sessionmaker(bind=engine)


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class Register(BaseModel):
    name: str
    password: str
class Login(BaseModel):
    name: str
    password: str
class Apply(BaseModel):
    name: str
    bonus_points: str
    desicribe: str
    picture: str



@app.post("/register")
async def register(register: Register):
    session = Session()
    password = base64.b64encode(register.password.encode())
    new_user = User(name=register.name, password=password,bonus_points = 100)
    session.add(new_user)
    session.commit()
    session.close()
    return {"code": 200, "message": "注册成功"}


SECRET_KEY = "sdifhgsiasfjaofhslio"
@app.post("/login")
async def login(login: Login):
    session = Session()
    password_ = base64.b64encode(login.password.encode())
    user = session.query(User).filter(User.name == login.name, User.password == password_).first()
    session.close()
    if user:
        token = jwt.encode({'user_name': user.name}, SECRET_KEY, algorithm='HS256')
        return {'token': token,"code": 200, "message": "登录成功"}
    else:
        return {"code": 400, "message": "登录失败"}




@app.post("/upload")
async def upload(file: UploadFile = File(...),text: str = None,token: str = Depends(oauth2_scheme)):
    contents = await file.read()
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).first()
        return username
    except jwt.PyJWTError:
        raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},)
    new_project = Project(name=user.name,bonus_points=user.bonus_points,describe=text,picture=contents)
    session.add(new_project)
    session.commit()
    session.close()
    return {"code": 200, "message": "上传成功"}


if __name__ == '__main__':
    uvicorn.run(app=app,host="127.0.0.1",port=3000)

