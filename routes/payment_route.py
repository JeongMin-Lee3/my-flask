import hashlib

from flask import Blueprint, render_template, request, jsonify
from database import get_db, close_db  # database.py 파일에서 get_db, close_db 함수를 가져옴

# 블루프린트 객체 생성
payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# user 테이블의 회원이 item 테이블의 상품을 구매하면 payment 테이블에 결제 정보가 저장되는 엔드포인트
# 1. 입력받은 회원 ID와 상품 ID, 사려는 개수(재고)가 실제로 존재하는지 확인
# 2. 회원이 충분한 돈을 가지고 있는지 확인: 회원 보유 포인트 >= 상품 가격 * 사려는 개수(cnt)
# 3. 2번 단계가 성공하면 user 테이블의 회원 보유 포인트(point)에서 상품 가격(price) * 사려는 개수(cnt)를 차감하고, item 테이블에서 사려는 개수(stock_cnt)를 차감
# 4. payment 테이블에 결제 정보를 저장

@payment_bp.route('/purchase', methods=['POST'])
def purchase():
    db = None
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': 'JSON body가 필요합니다.',
                'status_code': 400,
                'data': None
            })

        user_id = data.get('user_id')
        item_id = data.get('item_id')
        item_cnt = data.get('item_cnt')

        if not user_id or not item_id or not item_cnt:
            return jsonify({
                'success': False,
                'message': '회원님의 ID와 상품 ID, 구매하시려는 개수를 입력해주세요.',
                'status_code': 400,
                'data': None
            })

        db = get_db()

        # 회원과 상품 정보를 저장할 변수
        user = None
        item = None

        with db.cursor() as cursor:
            
            # 회원 조회
            cursor.execute("SELECT * FROM `user` WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({
                    'success': False,
                    'message': '회원 조회 실패, 회원이 존재하지 않습니다.',
                    'status_code': 400,
                    'data': None
                })

            # 회원(user테이블)의 status가 INACTIVE이면 결제 불가
            if user['status'] == 'INACTIVE':
                return jsonify({
                    'success': False,
                    'message': '회원님의 계정이 비활성화되어 결제가 불가능합니다.',
                    'status_code': 400,
                    'data': None
                })

            # 상품 조회
            cursor.execute("SELECT * FROM `item` WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            if not item:
                return jsonify({
                    'success': False,
                    'message': '상품 조회 실패, 상품이 존재하지 않습니다.',
                    'status_code': 400,
                    'data': None
                })

            # 상품 재고가 부족한지 확인
            if item['stock_cnt'] < item_cnt:
                return jsonify({
                    'success': False,
                    'message': '상품 재고가 부족합니다.',
                    'status_code': 400,
                    'data': None
                })
            
            # 회원이 충분한 돈을 가지고 있는지 확인
            if user['point'] < item['price'] * item_cnt:
                return jsonify({
                    'success': False,
                    'message': '회원님의 보유 포인트가 부족합니다.',
                    'status_code': 400,
                    'data': None
                })
            
            # 회원 보유 포인트에서 상품 가격 * 사려는 개수(cnt)를 차감하고, item 테이블에서 사려는 개수(stock_cnt)를 차감
            cursor.execute("UPDATE `user` SET point = point - %s WHERE id = %s", (item['price'] * item_cnt, user_id))
            cursor.execute("UPDATE `item` SET stock_cnt = stock_cnt - %s WHERE id = %s", (item_cnt, item_id))

            # 결제 정보를 저장 (total_price, user_id, item_id, cnt)
            cursor.execute("INSERT INTO `payment` (total_price, user_id, item_id, cnt) VALUES (%s, %s, %s, %s)", (item['price'] * item_cnt, user_id, item_id, item_cnt))
            
            db.commit() # 위 3개의 쿼리가 성공했을 때만 확정

            return jsonify({
                'success': True,
                'message': '결제 완료',
                'status_code': 200,
                'data': {
                    'total_price': item['price'] * item_cnt,
                    'user_id': user_id,
                    'item_id': item_id,
                    'cnt': item_cnt
                }
            })
    except Exception as e:
        print(e)
        if db:
            db.rollback()  # 포인트/재고/payment 중 하나라도 실패하면 전부 취소
        return jsonify({
            'success': False,
            'message': '결제 실패',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()


# 2. 결제 내역을 조회하는 라우트
@payment_bp.route('/get_payment_history', methods=['GET'])
def get_payment_history():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id는 필수입니다.',
                'status_code': 400,
                'data': None
            })
        
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `payment` AS p INNER JOIN `item` AS i ON p.item_id = i.id WHERE p.user_id = %s", (user_id,))
            payments = cursor.fetchall()
            return jsonify({
                'success': True,
                'message': '결제 내역 조회 완료',
                'status_code': 200,
                'data': payments
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '결제 내역 조회 실패',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()