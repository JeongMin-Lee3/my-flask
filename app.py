from flask import Flask, render_template
from flask import request
from routes.view_route import view_bp
from routes.test_route import test_bp
from routes.ai_route import ai_bp
from routes.car_route import car_bp
from routes.california_route import cali_bp

# Flask 애플리케이션 초기화
app = Flask(__name__)

# 블루프린트 등록 : 라우팅 그룹화
app.register_blueprint(view_bp)
app.register_blueprint(test_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(car_bp)
app.register_blueprint(cali_bp)

@app.route('/health', methods=['GET'])  # 서버 상태 확인하기 위한 엔드포인트
def health():
    return {
        'success': True,
        'message': 'Server is running',
        'status_code': 200,
        'version': '1.0.0'
    }

# 스크립트가 직접 실행될 때만 서버를 구동
if __name__ == '__main__':
    app.run(debug=True)


