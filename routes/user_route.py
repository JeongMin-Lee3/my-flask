import hashlib

from flask import Blueprint, render_template, request, jsonify
from database import get_db, close_db

# 블루프린트 객체 생성
user_bp = Blueprint('user', __name__, url_prefix='/api/user')


# 로그인하면 회원정보가 조회되거나, 존재하지 않으면 존재하지 않는 회원이라는 메시지가 출력되는 엔드포인트
@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        u_id = data.get('u_id')
        pw = data.get('pw')

        # 유효성 검사
        if not u_id or not pw:
            return jsonify({
                'success': False,
                'message': 'u_id, pw 는 필수입니다.',
                'status': 400,
                'data': None
            })

        pw_hash = hashlib.md5(pw.encode('utf-8')).hexdigest()

        # 회원 조회
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `user` WHERE u_id = %s", (u_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({
                    'success': False,
                    'message': '회원 조회 실패, 회원이 존재하지 않습니다.',
                    'status': 401,
                    'data': None
                })
            
            # 비밀번호 검사 (DB에 md5로 저장된 값과 비교)
            if user['pw'] != pw_hash:
                return jsonify({
                    'success': False,
                    'message': '비밀번호 오류',
                    'status': 400,
                    'data': None
                })
            
            return jsonify({
                'success': True,
                'message': '로그인 완료',
                'status': 200,
                'data': {
                    'id': user['id'],
                    'u_id': user['u_id'],
                    'nick': user['nick'],
                    'address': user['address'],
                }
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '로그인 실패',
            'status': 500,
            'data': None
        })
    finally:
        close_db()

#point 증가
@user_bp.route('/increase-point',methods=['PUT'])
def increase_point():
    try:
        data = request.get_json()
        id = data.get('id')
        point = data.get('amount')

        #유효성 검사
        if not id or not point:
            return jsonify({
                'success': False,
                'message': 'id, point 는 필수입니다.',
                'status': 400,
                'data': None
            })
        
        #회원 조회
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `user` WHERE id = %s", (id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({
                    'success': False,
                    'message': '회원 조회 실패, 회원이 존재하지 않습니다.',
                    'status': 400,
                    'data': None
                })
            
            #point 증가
            cursor.execute("UPDATE `user` SET point = point + %s WHERE id = %s", (point, id))
            db.commit()
            return jsonify({
                'success': True,
                'message': 'point 증가 완료',
                'status': 200,
                'data': {
                    'id': id,
                    'point': point
                }
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': 'point 증가 실패, 내부 서버 에러',
            'status': 500,
            'data': None
        })
    finally:
        close_db()

# 회원 비밀번호 수정
@user_bp.route('/update-password',methods=['PUT'])
def update_password():
    try:
        data = request.get_json()
        id = data.get('id')
        pw = data.get('new_pw')

        #유효성 검사
        if not id or not pw:
            return jsonify({
                'success': False,
                'message': 'id, new_pw 는 필수입니다.',
                'status': 400,
                'data': None
            })

        #회원 조회
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `user` WHERE id = %s", (id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({
                    'success': False,
                    'message': '회원 조회 실패, 회원이 존재하지 않습니다.',
                    'status': 400,
                    'data': None
                })
            
            #회원 비밀번호 수정
            cursor.execute("UPDATE `user` SET pw = md5(%s) WHERE id = %s", (pw, id))
            db.commit()
            return jsonify({
                'success': True,
                'message': '회원 비밀번호 수정 완료',
                'status': 200,
                'data': {
                    'id': id,
                    'pw': pw
                }
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '비밀번호 수정 실패',
            'status': 500,
            'data': None
        })
    finally:
        close_db()


#회원 address 수정
@user_bp.route('/update-address',methods=['PUT'])
def update_address():
    try:
        data = request.get_json()

        id = data.get('id')
        address = data.get('new_address')

        #유효성 검사
        if not id or not address:
            return jsonify({
                'success': False,
                'message': 'id, new_address 는 필수입니다.',
                'status': 400,
                'data': None
            })

        #회원 조회
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `user` WHERE id = %s", (id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({
                    'success': False,
                    'message': '회원 조회 실패, 회원이 존재하지 않습니다.',
                    'status': 400,
                    'data': None
                })
        
            #회원 address 수정
            cursor.execute("UPDATE `user` SET address = %s WHERE id = %s", (address, id))
            db.commit()
            return jsonify({
                'success': True,
                'message': '회원 address 수정 완료',
                'status': 200,
                'data': {
                    'id': id,
                    'address': address
                }
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '회원 address 수정 실패, 내부 서버 에러',
            'status': 500,
            'data': None
        })
    finally:
        close_db()



# 회원 생성
@user_bp.route('/create-user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'JSON body가 필요합니다.',
                'status_code': 400,
                'data': None
            })

        u_id = data.get('u_id')
        pw = data.get('pw')
        nick = data.get('nick')
        address = data.get('address')

        db = get_db()
        with db.cursor() as cursor:

            # u_id 중복 체크
            cursor.execute("SELECT * FROM `user` WHERE u_id = %s", (u_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({
                    'success': False,
                    'message': 'u_id 중복입니다.',
                    'status_code': 400,
                    'data': None
                })
            
            # nick 중복 체크
            cursor.execute("SELECT * FROM `user` WHERE nick = %s", (nick,))
            user = cursor.fetchone()
            if user:
                return jsonify({
                    'success': False,
                    'message': 'nick 중복입니다.',
                    'status_code': 400,
                    'data': None
                })

            cursor.execute(
                "INSERT INTO `user` (u_id, pw, nick, address, created_at) VALUES (%s, md5(%s), %s, %s, NOW())",
                (u_id, pw, nick, address)) # pw는 md5 해시 함수로 암호화
            db.commit()
        return jsonify({
            'success': True,
            'message': '회원 생성 완료, data는 생성된 회원 정보입니다.',
            'status_code': 200,
            'data': {
                'u_id': u_id,
                'pw': pw,
                'nick': nick,
                'address': address,
            }
        })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '회원 생성 실패',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()



# ID로 회원 조회
@user_bp.route('/get-user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try :
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `user` WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            return jsonify({
                'success': True,
                'message': '회원 조회 완료',
                'status_code': 200,
                'data': user
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '회원 조회 실패',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()



# 회원 전체 조회
@user_bp.route('/all', methods=['GET'])
def get_all_users():

    try :
        # 회원 전체 select
        db = get_db()  # db 연결
        # with 문을 사용하면 자동으로 커서를 닫고 db 연결을 닫습니다.
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `user`")
            users = cursor.fetchall()
            close_db()
            return jsonify({
                'success': True,
                'message': '회원 전체 조회 완료',
                'status_code': 200,
                'data': users
            })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '회원 전체 조회 실패',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()

    
    # cursor = db.cursor() # 커서 생성
    # cursor.execute("SELECT * FROM `user`") # 쿼리 실행
    # users = cursor.fetchall() # 쿼리 결과 반환
    # cursor.close() # 커서 닫기
    # close_db() # db 연결 닫기

    