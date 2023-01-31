import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt

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
    desicribe = Column(String(20))
    picture = Column(String(20))

Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
DBSession = sessionmaker(bind=engine)


app = FastAPI()

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
    new_user = User(name=register.name, password=register.password,bonus_points = 100)
    session.add(new_user)
    session.commit()
    session.close()
    return {"code": 200, "message": "注册成功"}


@app.post("/login")
async def login(login: Login):
    session = Session()
    user = session.query(User).filter(User.name == login.name, User.password == login.password).first()
    session.close()
    if user:
        token = jwt.encode({'user_name': user.name}, 'secret', algorithm='HS256')
        return {'token': token,"code": 200, "message": "登录成功"}
    else:
        return {"code": 400, "message": "登录失败"}






if __name__ == '__main__':
    uvicorn.run(app=app,host="127.0.0.1",port=3000)

