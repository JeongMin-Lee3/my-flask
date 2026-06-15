import hashlib

from flask import Blueprint, render_template, request, jsonify
from database import get_db, close_db  # database.py 파일에서 get_db, close_db 함수를 가져옴

# 블루프린트 객체 생성
item_bp = Blueprint('item', __name__, url_prefix='/api/item')

# 1. 일단 등록된 item 목록을 쭉 보여주는 라우트
@item_bp.route('/get_all_list', methods=['GET'])

def get_all_list():
    try:
        db = get_db()

        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `item`")
            items = cursor.fetchall()
            close_db()
            return jsonify({
                'success' : True,
                'message' : "전체 상품 조회 완료",
                'status_code' : 200,
                'data' : items
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success' : False,
            'message' : "전체 상품 조회에 실패했습니다.",
            'status_code' : 500,
            'data' : None
        })
    finally:
        close_db()


# 2. item 테이블의 상품명, 설명, 제조사, 가격을 수정할 수 있는 라우트

@item_bp.route('/advise', methods=['PUT'])

def advise():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': '요청 데이터가 없습니다.',
                'status_code': 400,
                'data': None
            })

        id = data.get('id')
        if not id:
            return jsonify({
                'success': False,
                'message': 'id는 필수입니다.',
                'status_code': 400,
                'data': None
            })

        # body에 포함된 필드만 수정 (name, description, maker, price 중 하나 이상)
        updatable_fields = ('name', 'description', 'maker', 'price')
        updates = {key: data[key] for key in updatable_fields if key in data}

        if not updates:
            return jsonify({
                'success': False,
                'message': '수정할 값을 하나 이상 입력해주세요',
                'status_code': 400,
                'data': None
            })

        db = get_db()

        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `item` WHERE id = %s", (id,))
            item = cursor.fetchone()
            if not item:
                return jsonify({
                    'success' : False,
                    'message' : "상품 조회 실패, 상품이 존재하지 않습니다.",
                    'status_code' : 400,
                    'data' : None
                })
            set_clause = ", ".join(f"`{key}` = %s" for key in updates)
            values = list(updates.values()) + [id]
            cursor.execute(f"UPDATE `item` SET {set_clause} WHERE id = %s", values)
            db.commit()
            return jsonify({
                'success' : True,
                'message' : "상품 수정 완료",
                'status_code' : 200,
                'data' : None
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success' : False,
            'message' : "상품 수정에 실패했습니다.",
            'status_code' : 500,
            'data' : None
        })
    finally:
        close_db()

# 3. 상품 등록
@item_bp.route('/create', methods=['POST'])
def create():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '요청 데이터가 없습니다.',
                'status_code': 400,
                'data': None
            })

        name = data.get('name')
        description = data.get('description')
        maker = data.get('maker')
        price = data.get('price')
        stock_cnt = data.get('stock_cnt')

        if not name or not description or not maker or not price or not stock_cnt:
            return jsonify({
                'success': False,
                'message': 'name, description, maker, price, stock_cnt는 필수입니다.',
                'status_code': 400,
                'data': None
            })
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO `item` (name, description, maker, price, stock_cnt) VALUES (%s, %s, %s, %s, %s)", (name, description, maker, price, stock_cnt))
            db.commit()
            return jsonify({   
                'success': True,
                'message': '상품 등록 완료',
                'status_code': 200,
                'data': {
                    'name': name,
                    'description': description,
                    'maker': maker,
                    'price': price
                }
            })
    except Exception as e: 
        print(e)
        return jsonify({
            'success': False,
            'message': '상품 등록에 실패했습니다.',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()

# 4. 어떤 상품을 조회하면 그 상품을 구매한 사용자 목록을 조회하는 라우트
@item_bp.route('/get_purchase_list', methods=['GET'])
def get_purchase_list():
    try:
        id = request.args.get('id')
        if not id:
            return jsonify({
                'success': False,
                'message': 'id는 필수입니다.',
                'status_code': 400,
                'data': None
            })  

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `payment` AS p INNER JOIN `item` AS i ON p.item_id = i.id WHERE p.item_id = %s", (id,))
            payments = cursor.fetchall()
            return jsonify({
                'success' : True,
                '메세지' : "구매 목록 조회 완료",
                'status_code' : 200,
                'data' : payments
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success' : False,
            'message' : "구매 목록 조회에 실패했습니다.",
            'status_code' : 500,
            'data' : None
        })
    finally:
        close_db()