# iris 붓꽃 종류 예측 모델 _ 외부에서 만든 모델 사용
import os

from flask import Blueprint, request, jsonify
import joblib
import numpy as np
from database import get_db, close_db

# 블루프린트 객체 생성
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'iris_model_0610.pkl')
loaded_model = joblib.load(MODEL_PATH)

CLASS_NAMES = ['setosa', 'versicolor', 'virginica']


def serialize_iris_row(row): # 붓꽃 예측 데이터 조회 라우트에서 사용
    if not row:
        return row
    result = dict(row)
    if result.get('created_at') is not None:
        result['created_at'] = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    return result


# 붓꽃 예측 라우트
@ai_bp.route('/predict-iris', methods=['POST'])

def predict_iris():
    db = None
    try:
        data = request.get_json()
        # 유효성 검사
        if not data:
            return jsonify({
                'success': False,
                'message': 'JSON body가 필요합니다.',
                'status_code': 400,
                'data': None
            })
        # 필수 입력 사항 검사
        if any(data.get(key) is None for key in ('sepal_length', 'sepal_width', 'petal_length', 'petal_width')):
            return jsonify({
                'success': False,
                'message': 'sepal_length, sepal_width, petal_length, petal_width 는 필수입니다.',
                'status_code': 400,
                'data': None
            })

        sepal_length = float(data.get('sepal_length'))
        sepal_width = float(data.get('sepal_width'))
        petal_length = float(data.get('petal_length'))
        petal_width = float(data.get('petal_width'))
        
        # 예측 모델 적용
        temp_X = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
        class_number = int(loaded_model.predict(temp_X)[0])

        # 예측 결과 유효성 검사
        if class_number < 0 or class_number >= len(CLASS_NAMES):
            return jsonify({
                'success': False,
                'message': '예측 결과가 유효하지 않습니다.',
                'status_code': 500,
                'data': None
            })

        # 예측 결과 클래스 이름 저장
        class_name = CLASS_NAMES[class_number]

        db = get_db()

        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO `iris_data`
                    (sepal_length, sepal_width, petal_length, petal_width, class_number, class_name, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (sepal_length, sepal_width, petal_length, petal_width, class_number, class_name),
            )
            db.commit()
            iris_id = cursor.lastrowid

        return jsonify({
            'success': True,
            'message': '붓꽃 종류 예측 완료',
            'status_code': 200,
            'data': {
                'id': iris_id,
                'sepal_length': sepal_length,
                'sepal_width': sepal_width,
                'petal_length': petal_length,
                'petal_width': petal_width,
                'class_number': class_number,
                'class_name': class_name,
            }
        })
    except Exception as e:
        print(e)
        if db:
            db.rollback()
        return jsonify({
            'success': False,
            'message': '붓꽃 종류 예측 실패',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()

# 붓꽃 예측 데이터 조회 라우트
@ai_bp.route('/iris-data', methods=['GET'])
def get_iris_data():
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM `iris_data` ORDER BY id DESC")
            rows = cursor.fetchall()

        return jsonify({
            'success': True,
            'message': '붓꽃 예측 데이터 조회 완료',
            'status_code': 200,
            'data': [serialize_iris_row(row) for row in rows]
        })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'message': '붓꽃 예측 데이터 조회 실패',
            'status_code': 500,
            'data': None
        })
    finally:
        close_db()
