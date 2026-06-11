from flask import Blueprint, request
import joblib
import numpy as np
import pandas as pd

# 블루프린트 객체 생성
car_bp = Blueprint('car', __name__, url_prefix='/api/car')

loaded_model = joblib.load('./models/car_model_ver_1.0.0.pkl')

@car_bp.route('/predict-car', methods=['POST'])
def predict_car():

    data = request.get_json()

    bagi = data.get('bagi')
    weight = data.get('weight')
    cylinder = data.get('cylinder')

    if not bagi or not weight or not cylinder:
        return {
            'success': False,
            'message': '배기량, 중량, 기통수는 필수 입력 사항입니다.',
            'status': 400,
            'data': None
        }
    
    # 예측 (학습 시와 동일하게 컬럼명있는 DataFrame으로 넣어 컬럼명·순서 일치)
    temp_X = pd.DataFrame([[bagi, weight, cylinder]], columns=loaded_model.feature_names_in_)
    temp_y_pred = loaded_model.predict(temp_X)
    return {
        'success': True,
        'message': '연비 예측 완료',
        'status': 200,
        'data': {
            '연비': temp_y_pred[0]
        }
    }