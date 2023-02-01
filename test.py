import jwt
SECRET_KEY = "sdifhgsiasfjaofhslio"
token ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiJoYXNoIn0.LgIV5GDjfuQY24GcW0okoqdbXVqRiVPC0_D2cfygHPY"
payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
username: str = payload.get("user_name")
print(username)