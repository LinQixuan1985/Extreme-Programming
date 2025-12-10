import os

class Config:
    # 使用 MySQL 8.0，确保支持 JSON 类型
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:MySQL80@localhost/contacts_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-for-flask'