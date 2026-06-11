from flask import request, Blueprint
from joblib.parallel import method
import pandas as pd
import joblib

# 블루프린트 객체 생성
cali_bp = Blueprint('cali', __name__, url_prefix='/api/cali')

loaded_model = joblib.load('./models/california_house_model.pkl')

@cali_bp.route('/predict-houseprice', methods=['POST'])

def predict_houseprice():
    data = request.get_json()

    Longitude = data.get('longitude')
    Latitude = data.get('latitude')
    HouseAge = data.get('housing_median_age')
    AveRooms = data.get('total_rooms')
    AveBedrooms = data.get('total_bedrooms')
    Population = data.get('population')
    AveOccup = data.get('households')
    Population = data.get('median_income')
    
    if not Longitude or not Latitude or not HouseAge or not AveRooms or not AveBedrooms or not Population or not AveOccup or not Population:
        return {
            'success': False,
            'message': 'Longitude, Latitude, HouseAge, AveRooms, AveBedrooms, Population, AveOccup, Population는 필수 입력 사항입니다.',
            'status': 400,
            'data': None
        }
    
    temp_X = pd.DataFrame([[Longitude, Latitude, HouseAge, AveRooms, AveBedrooms, Population, AveOccup, Population]], columns=loaded_model.feature_names_in_)
    temp_y_pred = loaded_model.predict(temp_X)
    return {
        'success': True,
        'message': '주택 가격 예측 완료',
        'status': 200,
        'data': {
            '주택 가격': temp_y_pred[0]
        }
    }