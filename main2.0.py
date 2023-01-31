from fastapi import FastAPI
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker

# 初始化FastAPI
app = FastAPI()

# 初始化MySQL连接
engine = create_engine('mysql://username:password@host/database')

# 初始化ORM
Base = declarative_base()

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 定义用户模型
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    password = Column(String(255))

# 创建用户
@app.post('/register')
def register(username: str, password: str):
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return {'message': 'User created successfully!'}

# 登录
@app.post('/login')
def login(username: str, password: str):
    user = session.query(User).filter_by(username=username).first()
    if not user or not user.password == password:
        return {'message': 'Incorrect username or password'}
    else:
        # 生成JWT
        token = jwt.encode({'user_id': user.id}, 'secret', algorithm='HS256')
        return {'token': token}
