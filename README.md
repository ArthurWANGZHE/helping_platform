# helping_platform

### ORM相关
即自动生成mysql注入语句
使用sqlalchemy create engine语句
实现了注册时保存信息（1/23）

### JWT加密
使用jwt包
在验证成功后形成token（1/30）

### 对密码保存添加哈希加密
#### 问题：一开始对哈希函数没有做区分，导致一开始加密后长度过长无法保存
哈希加密有可以加密成不同位数
尝试了hashlib，base64，cryptography三种加密库
最后使用了base64实现了对于储存数据的加密保存（1/31）
