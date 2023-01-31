import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import jwt


'''
mysql是数据库，pymysql是用来连接数据库的包，root是数据库的用户名，usbw是密码，jdbc是数据库的名称，utf8是编码方式。
'''
engine = create_engine("mysql+pymysql://root:usbw@127.0.0.1:3307/jdbc?charset=utf8", max_overflow=5)
Base = declarative_base()

# 创建单表
class Users(Base):
	# 表名
    __tablename__ = 'users'
    # 列名
    # 主键，自增，非空，默认值，索引，唯一索引。
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False, default="sds", index=True)
    email = Column(String(16), nullable=False, unique=True)
    # 设置联合索引，联合主键等
    __table_args__ = (
        # 联合唯一索引，名字写后面
        UniqueConstraint('id', 'name', name='uix_id_name'),
        # 联合普通索引,名字写前面
        Index('ix_id_name', 'name', 'email'),
    )
class Tech(Base):
    __tablename__ = 'techs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False, default="sds", index=True)
    # 外键
    uid = Column(Integer, ForeignKey("users.id"))
    # 带外键的表和与之相关联的表建立一个关系
    users_tech = relationship("Users",backref="xxoo")

def creat_db():
    # 把所有继承Base的类全部都生成一张表
    Base.metadata.create_all(engine)
def drop_db():
    Base.metadata.drop_all(engine)

首先通过引擎获得一个数据库的连接
Session = sessionmaker(bind=engine)
session = Session()
# 增加
	# 增加单行
obj1 = Users(name="weweewe",email="wwwww")
session.add(obj1)
	# 增加多行
objs = [
Users(name="12",email="21"),
Users(name="13",email="22"),
Users(name="14",email="23")
]
session.add_all(objs)
# 查询
	# 查询所有
print(session.query(Users))
user_list = session.query(Users).all()
for row in user_list:
    print(row.id,row.name,row.email)
	# 条件查询
user_list = session.query(Users).filter(Users.id>3)
for row in user_list:
    print(row.id,row.name,row.email)
	# 取任意列
user_list = session.query(Users.id,Users.name).filter(Users.id>3)
for row in user_list:
    print(row.id,row.name)
# 删除
session.query(Users).filter(Users.id==5).delete()
# 修改:
	# 字典，参数名：值
session.query(Users).filter(Users.id==4).update({"name":"ijii"})
	# 根据处理的类型不同，synchronize_session选择不同的值
		# 字符串
session.query(Users).filter(Users.id > 0).update({Users.name: Users.name + "X"}, synchronize_session=False)
		# 数字
session.query(Users).filter(Users.id > 0).update({"num": Users.num + 20}, synchronize_session="evaluate")

# filter_by中的传的是参数，不是表达式，filter传的是表达式
ret = session.query(Users).filter_by(name='alex').all()
# and
ret = session.query(Users).filter(Users.id > 1, Users.name == 'eric').all()
# between and
ret = session.query(Users).filter(Users.id.between(1, 3), Users.name == 'eric').all()
# in
ret = session.query(Users).filter(Users.id.in_([1,3,4])).all()
# not in
ret = session.query(Users).filter(~Users.id.in_([1,3,4])).all()
# 嵌套查询
ret = session.query(Users).filter(Users.id.in_(session.query(Users.id).filter_by(name='eric'))).all()
from sqlalchemy import and_, or_
# and
ret = session.query(Users).filter(and_(Users.id > 3, Users.name == 'eric')).all()
# or
ret = session.query(Users).filter(or_(Users.id < 2, Users.name == 'eric')).all()
# and 和 or 的综合使用
ret = session.query(Users).filter(
    or_(
        Users.id < 2,
        and_(Users.name == 'eric', Users.id > 3),
        Users.extra != ""
    )).all()

# 通配符
ret = session.query(Users).filter(Users.name.like('e%')).all()
ret = session.query(Users).filter(Users.name.like('e_')).all()
# ~代表非
ret = session.query(Users).filter(~Users.name.like('e%')).all()

# 限制
ret = session.query(Users)[1:2]

# 排序
ret = session.query(Users).order_by(Users.name.desc()).all()
ret = session.query(Users).order_by(Users.name.desc(), Users.id.asc()).all()

# 分组
from sqlalchemy.sql import func

ret = session.query(Users).group_by(Users.extra).all()
ret = session.query(
    func.max(Users.id),
    func.sum(Users.id),
    func.min(Users.id)).group_by(Users.name).all()
ret = session.query(
    func.max(Users.id),
    func.sum(Users.id),
    func.min(Users.id)).group_by(Users.name).having(func.min(Users.id) >2).all()

# 连表
# 笛卡尔积
ret = session.query(Users,Tech)
# 等值连接
ret = session.query(Users, Tech).filter(Users.id == Tech.uid).all()
# 自然连接，自动连接外键
ret = session.query(Users).join(Tech).all()
# 左外连接
ret = session.query(Users).join(Tech, isouter=True).all()

# 组合
# 去重组合
q1 = session.query(Users.name).filter(Users.id > 2)
q2 = session.query(Tech.name).filter(Tech.uid < 2)
ret = q1.union(q2).all()
# 不去重组合
q1 = session.query(Users.name).filter(Users.id > 2)
q2 = session.query(Tech.caption).filter(Tech.uid < 2)
ret = q1.union_all(q2).all()
session.commit()
session.close()
# 子查询
# 这就可以把q1当成表，来进行查询
# subquery()使查询结果作为一个表来使用
q1 = session.query(Users).filter(Users.id>2).subquery()
rs1 = session.query(q1).all()
# as_scalar()使查询结果作为一项来使用
rs2 = session.query(Users.id,session.query(Tech.id).as_scalar()).all()

'''
relationship的作用（在带有外键的类中添加）
    1、正向操作
    2、反向操作
'''
# 问题1：获取用户的信息和与其关联表的信息
# 1、连接表操作。
user_list = session.query(Users, Tech).join(Tech).all()
for row in user_list:
    print(row[0].id, row[0].name, row[1].name)

user_list = session.query(Users.id, Users.name, Tech.name).join(Tech).all()
for row in user_list:
    print(row[0], row[1], row[2])
    # 也可以用row.属性名的时候拿到，当两个表中的属性名一样时，只能拿一个。
    print(row.id, row.name)
# 下面的语句(不加.all())，直接打印的话是SQL语句，如果放在for循环中，他也是一个迭代器，
# 可以实现一个一个的拿，如果后面加了.all()，就会一下子把所有的查询结果都放到了变量中。
user_list = session.query(Users.id, Tech.name).join(Tech)
print(user_list)
for row in user_list:
    print(row.id)

# 2、在带有外键的类中添加一个与与之关联的表的关系，可以实现自动的连表。不用再写join
# （正向操作）
user_list = session.query(Tech)
for row in user_list:
    # 通过row.users_tech.属性名来获取与之关联表的属性值
    print(row.id, row.name, row.users_tech.name, row.users_tech.email)

# 问题2：一个Users下有多个Tech(1对多的关系)，要求获取Users信息和属于这个用户的Tech信息
#       1、嵌套
tech_list = session.query(Users)
for row in tech_list:
    print(row.id, row.name, row.email, session.query(Tech).filter(row.id == Tech.uid).all())
    # 2、利用两表之间的relationship来关联,(效果和第一种一样)
    # （反向操作）
tech_list = session.query(Users)
for row in tech_list:
    print(row.id, row.name, row.email, row.xxoo)
