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

"""

import jwt
SECRET_KEY = "sdifhgsiasfjaofhslio"
token ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiJoYXNoIn0.LgIV5GDjfuQY24GcW0okoqdbXVqRiVPC0_D2cfygHPY"
payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
username: str = payload.get("user_name")
print(username)

"""
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt
import base64
from starlette.status import HTTP_401_UNAUTHORIZED

"""
Base = declarative_base()
engine = create_engine('mysql://root:123456@127.0.0.1:3306/db', echo=True)
class User(Base):
    __tablename__ = 'user'
    name = Column(String(20), primary_key=True)
    password = Column(String(50), primary_key=True)
    bonus_points = Column(Integer)
    level = Column(String(2))

Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
DBSession = sessionmaker(bind=engine)

session = Session()
new_user = User(name="administrator", password="ad123", bonus_points=0, level=1)
session.add(new_user)
session.commit()
session.close()

import mysql.connector
db=mysql.connector.connect(host="127.0.0.1", user="root", password="123456",database="db")

cursor=db.cursor()

query="ALTER TABLE user ADD level VARCHAR(100)"
cursor.execute(query)
db.commit()
print("添加了新列..")

db.close()


session = Session()
project_list = session.query(Project).filter(Project.status == 1)
session.close()
"""
