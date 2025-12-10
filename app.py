# app.py
from flask import Flask, request, jsonify
from config import Config
from models import db, Contact
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 生产环境应限制来源
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


def parse_contact_data(data):
    """从请求数据中提取并验证联系人字段"""
    if not isinstance(data, dict):
        return None, "无效的数据格式"

    contact = Contact()
    contact.name = data.get('name', '').strip()
    contact.phone_numbers = data.get('phone_numbers', [])
    contact.emails = data.get('emails', [])
    contact.addresses = data.get('addresses', [])
    contact.socials = data.get('socials', [])
    contact.is_bookmarked = bool(data.get('is_bookmarked', False))
    return contact, None


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.all()
    return jsonify({
        'success': True,
        'message': '获取成功',
        'data': [c.to_dict() for c in contacts]
    })


@app.route('/api/contacts/<int:id>', methods=['GET'])
def get_contact(id):
    contact = Contact.query.get_or_404(id, description="联系人不存在")
    return jsonify({
        'success': True,
        'message': '获取成功',
        'data': contact.to_dict()
    })


@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    contact, error = parse_contact_data(data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    is_valid, msg = contact.validate()
    if not is_valid:
        return jsonify({'success': False, 'message': msg}), 400

    # 检查电话号码是否与其他联系人重复（任一号码重复即冲突）
    for phone in contact.phone_numbers:
        existing = Contact.query.filter(Contact.phone_numbers.contains(phone)).first()
        if existing:
            return jsonify({'success': False, 'message': f'电话号码 {phone} 已被使用'}), 409

    try:
        db.session.add(contact)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '创建成功',
            'data': contact.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500


@app.route('/api/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    contact = Contact.query.get_or_404(id, description="联系人不存在")
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无数据'}), 400

    # 不允许修改 ID
    new_contact, error = parse_contact_data(data)
    if error:
        return jsonify({'success': False, 'message': error}), 400

    # 验证新数据
    is_valid, msg = new_contact.validate()
    if not is_valid:
        return jsonify({'success': False, 'message': msg}), 400

    # 检查电话号码是否与其他联系人（除自己外）重复
    for phone in new_contact.phone_numbers:
        existing = Contact.query.filter(
            Contact.id != id,
            Contact.phone_numbers.contains(phone)
        ).first()
        if existing:
            return jsonify({'success': False, 'message': f'电话号码 {phone} 已被其他联系人使用'}), 409

    # 更新字段
    contact.name = new_contact.name
    contact.phone_numbers = new_contact.phone_numbers
    contact.emails = new_contact.emails
    contact.addresses = new_contact.addresses
    contact.socials = new_contact.socials
    contact.is_bookmarked = new_contact.is_bookmarked

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': contact.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '更新失败'}), 500


@app.route('/api/contacts/<int:id>/bookmark', methods=['POST'])
def toggle_bookmark(id):
    """单独接口用于切换收藏状态（也可合并到 PUT，但分离更清晰）"""
    contact = Contact.query.get_or_404(id, description="联系人不存在")
    data = request.get_json()
    if not data or 'is_bookmarked' not in data:
        return jsonify({'success': False, 'message': '缺少 is_bookmarked 字段'}), 400

    contact.is_bookmarked = bool(data['is_bookmarked'])
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '收藏状态更新成功',
            'data': {'is_bookmarked': contact.is_bookmarked}
        })
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': '更新失败'}), 500


@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id, description="联系人不存在")
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': '删除失败'}), 500


# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': str(error.description)}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)