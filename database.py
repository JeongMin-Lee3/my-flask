from flask import g
import pymysql

db_config = {
    'host': 'localhost',  # 3.36.28.140 강사님 서버
    'port': 3306,
    'user': 'root',         # jmcoding 
    'password': 'Mdb@Pass94!2', # 123qwe! 강사님 서버 비밀번호
    'db': 'alpha_shop_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    # 현재 요청(Request) 컨텍스트에 db 연결이 없으면 생성
    if 'db' not in g:
        g.db = pymysql.connect(**db_config)
    return g.db

def close_db(e=None):
    # 요청이 끝날 때 db 연결이 열려있으면 닫음
    db = g.pop('db', None)
    if db is not None:
        db.close()