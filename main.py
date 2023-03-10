import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt
import base64

from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED


Base = declarative_base()
engine = create_engine('mysql://root:123456@127.0.0.1:3306/db', echo=True)


class User(Base):
    __tablename__ = 'users'
    name = Column(String(20), primary_key=True)
    password = Column(String(50))
    bonus_points = Column(Float)
    level = Column(String(2))





class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    project_name = Column(String(20))
    bonus_points = Column(String(20))
    describe = Column(String(20))
    picture = Column(Text)
    donation = Column(String(20))
    status = Column(String(20))


# 0：提交申请；1：申请通过；2：申请不通过；3：个人设置不公开
class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    path = Column(String(100))

Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
DBSession = sessionmaker(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class Register(BaseModel):
    name: str
    password: str


class Login(BaseModel):
    name: str
    password: str


class Apply(BaseModel):
    project_name: str
    bonus_points: str
    description: str
    picture: str


class Detail(BaseModel):
    project_name: str


@app.post("/register")
async def register(register: Register):
    session = Session()
    password = base64.b64encode(register.password.encode())
    new_user = User(name=register.name, password=password, bonus_points=100, level=0)
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
async def upload(file: UploadFile = File(...), project_name: str = None, description: str = None,
                 token: str = Depends(oauth2_scheme)):
    contents = await file.read()
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).first()
        if user:
            file_name = file.filename
            file_path = f"D:\Developer\coding\data\{file_name}"
            with open(file_path, "wb") as f:
                f.write(file.file.read())
            image = Image(name=file_name, path=file_path)
            new_project = Project(project_name=project_name, name="arthur", bonus_points=100, describe=description,
                                  picture=file_path, donation=0, status=0)
            session.add(image)
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



"""
@app.post("/upload")
async def upload(file: UploadFile = File(...), project_name: str = None, description: str = None,
                 ):
    session = Session()
    file_name = file.filename
    file_path = f"D:\Developer\coding\data\{file_name}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    image = Image(name=file_name, path=file_path)
    new_project = Project(project_name=project_name, name="arthur", bonus_points=100, describe=description,
                          picture=file_path, donation=0, status=0)
    session.add(image)
    session.add(new_project)
    session.commit()
    session.close()
    return {"code": 200, "message": "上传成功"}
"""

@app.get("/show_all")
async def show_all(token: str = Depends(oauth2_scheme)):
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        user = session.query(User).filter(User.name == username).first()
        if user:
            project_list = []
            projects = session.query(Project).filter(Project.status == 1).all()
            for item in projects:
                project_list.append(item.project_name)
            session.close()
            print(project_list)
            return f"{{\"message\":\"{project_list}\"}}"

    except jwt.PyJWTError:
        session.close()
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}, )

"""
@app.get("/show_all")
async def show_all():
    session = Session()
    project_list = []
    projects = session.query(Project).filter(Project.status == 1).all()
    for item in projects:
        project_list.append(item.project_name)
    session.close()
    print(project_list)
    return f"{{\"message\":\"{project_list}\"}}"
"""


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

"""
@app.get("/show_mine")
async def show_mine():
    session = Session()
    username = "arthur"
    project_list = []
    projects = session.query(Project).filter(Project.name == username).all()
    for item in projects:
        img_stream = ''
        with open(item.picture, 'rb') as img_f:
            img_stream = img_f.read()
            img_stream = base64.b64encode(img_stream).decode()
        a_project = [item.project_name, img_stream]
        project_list.append(a_project)
    session.close()
    print(project_list)
    return f"{{\"message\":\"{project_list}\"}}"
"""


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
"""
@app.post("/detail")
async def detail(detail: Detail):
    session = Session()
    project = session.query(Project).filter(Project.project_name == detail.project_name).first()
    project_name = detail.project_name
    name = project.name
    bonus_points = project.bonus_points
    describe = project.describe
    picture = project.picture
    donation = project.donation
    session.commit()
    session.close()
    print(project_name, name, bonus_points, describe, picture, donation)
    return {"code": 200, "message": "搜索成功"}

"""
@app.api_route("/donate", methods=["GET", "PATCH"])
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
"""
@app.patch("/donate")
async def donate(detail: Detail, text1: str = None):
    session = Session()

    username = "arthur"
    user = session.query(User).filter(User.name == username).first()
    project = session.query(Project).filter(Project.project_name == detail.project_name).first()
    donation = project.donation
    donations = text1
    donation = int(donations) + int(donation)
    project.donation = donation
    user.bonus_points += int(donations) / 10
    session.query(User).filter(User.name == user.name).update({"bonus_points": "user.bonus_points"})
    session.query(Project).filter(Project.name == project.name).update({"donation": "donation"})
    session.commit()
    session.close()
    return {"code": 200, "message": "捐赠成功"}
"""
@app.patch("/invest")
async def invest(detail: Detail, result_status: str = None, token: str = Depends(oauth2_scheme)):
    session = Session()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        username: str = payload.get("user_name")
        userlevel = payload.get("user_level")
        user = session.query(User).filter(User.name == username).first()
        if user:
            if userlevel > 0:
                if result_status == 1:
                    detail.status = result_status
                    session.commit()
                    session.close()
                return {"code": 200, "message": "申请通过，修改成功"}
                if result_status == 2:
                    detail.status = result_status
                    session.commit()
                    session.close()
                return {"code": 200, "message": "申请不通过，修改成功"}
            else:
                return {"code": 401, "message": "您没有修改权限"}
    except jwt.PyJWTError:
        session.close()
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}, )


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=3000)
