import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
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
    __tablename__ = 'users'
    name = Column(String(20), primary_key=True)
    password = Column(String(50), primary_key=True)
    bonus_points = Column(Integer)
    level = Column(String(2))


class Project(Base):
    __tablename__ = 'project'
    name = Column(String(20), primary_key=True)
    project_name = Column(String(20))
    bonus_points = Column(String(20))
    describe = Column(String(20))
    picture = Column(String(20))
    donation = Column(String(20))
    status = Column(String(20))
#0：提交申请；1：申请通过；2：申请不通过；3：个人设置不公开


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


class Detail(BaseModel):
    project_name: str


@app.post("/register")
async def register(register: Register):
    session = Session()
    password = base64.b64encode(register.password.encode())
    new_user = User(name=register.name, password=password, bonus_points=100, level = 0)
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
        token = jwt.encode({'user_name': user.name, 'user_level': user.level}, SECRET_KEY, algorithm='HS256')
        return {'token': token, "code": 200, "message": "登录成功"}
    else:
        return {"code": 400, "message": "登录失败"}


@app.post("/upload")
async def upload(file: UploadFile = File(...), text1: str = None, text2: str = None,
                 token: str = Depends(oauth2_scheme)):
    contents = await file.read()
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).first()
        if user:
            new_project = Project(project_name=text1, name=user.name, bonus_points=user.bonus_points, describe=text2,
                                  picture=contents, donation=0, status = 0)
            session.add(new_project)
            session.commit()
            session.close()
            return {"code": 200, "message": "上传成功"}
    except jwt.PyJWTError:
        session.close()
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}, )


@app.get("/show_all")
async def show_all(token: str = Depends(oauth2_scheme)):
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).filter(Project.status == 1)
        if user:
            project_list = session.query(Project).all()
            return project_list

    except jwt.PyJWTError:
        session.close()
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}, )


@app.get("/show_mine")
async def show_mine(token: str = Depends(oauth2_scheme)):
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).first()
        if user:
            project_list = session.query(Project).filter(Project.name == username)
            return project_list

    except jwt.PyJWTError:
        session.close()
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}, )


@app.get("/detail")
async def detail(detail: Detail, token: str = Depends(oauth2_scheme)):
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).first()
        if user:
            project_name = detail.project_name
            name = detail.name
            bonus_points = detail.bonus_points
            describe = detail.descriebe
            picture = detail.picture
            donation = detail.donation
            session.commit()
            session.close()
            return project_name, name, bonus_points, describe, picture, donation
    except jwt.PyJWTError:
        session.close()
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}, )


@app.api_route("/donate", methods=["GET", "POST"])
async def donate(detail: Detail, text1: str = None, token: str = Depends(oauth2_scheme)):
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).first()
        if user:
            project_name = detail.project_name
            donation = detail.donation
            donations = text1
            donation = int(donations) + int(donation)
            detail.donation = donation
            user.bonus_points += int(donations) / 10
            session.query(User).filter(User.name == username).update({"bonus_points": "user.bonus_points"})
            session.query(Project).filter(Project.name == project_name).update({"donation": "donation"})
            session.commit()
            session.close()
            return {"code": 200, "message": "捐赠成功"}
    except jwt.PyJWTError:
        session.close()
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}, )


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=3000)
