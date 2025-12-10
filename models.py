from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON  # MySQL 特有 JSON 类型

db = SQLAlchemy()

class Contact(db.Model):
    __tablename__ = 't_contact'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # 使用 JSON 字段存储多个联系方式（MySQL 5.7+ 支持）
    phone_numbers = db.Column(JSON, nullable=False, default=list)  # 必须至少一个
    emails = db.Column(JSON, nullable=False, default=list)
    addresses = db.Column(JSON, nullable=False, default=list)
    socials = db.Column(JSON, nullable=False, default=list)
    
    is_bookmarked = db.Column(db.Boolean, default=False, nullable=False)

    # 时间戳（可选）
    created_time = db.Column(db.DateTime, server_default=db.func.now())
    updated_time = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone_numbers': self.phone_numbers or [],
            'emails': self.emails or [],
            'addresses': self.addresses or [],
            'socials': self.socials or [],
            'is_bookmarked': self.is_bookmarked
        }

    def validate(self):
        """简单校验：至少一个电话号码，姓名非空"""
        if not self.name or not self.name.strip():
            return False, "姓名不能为空"
        if not self.phone_numbers or not isinstance(self.phone_numbers, list) or len(self.phone_numbers) == 0:
            return False, "至少需要一个电话号码"
        # 简单去重和清理
        self.phone_numbers = [str(p).strip() for p in self.phone_numbers if str(p).strip()]
        self.emails = [str(e).strip() for e in (self.emails or []) if str(e).strip()]
        self.addresses = [str(a).strip() for a in (self.addresses or []) if str(a).strip()]
        self.socials = [str(s).strip() for s in (self.socials or []) if str(s).strip()]
        if not self.phone_numbers:
            return False, "电话号码不能为空"
        return True, ""