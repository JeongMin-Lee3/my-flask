from flask import Blueprint, render_template

# 블루프린트 객체 생성
view_bp = Blueprint('view', __name__, url_prefix='/')

# 페이지 호출
@view_bp.route('/')
def index():
    return render_template('index.html')

@view_bp.route('/signup')
def signup():
    return render_template('signup.html')

@view_bp.route('/basic-1')
def basic_1():
    return render_template('basic-1.html')

@view_bp.route('/class-id')
def class_id():
    return render_template('class-id.html')

@view_bp.route('/layout')
def layout():
    return render_template('layout.html')

@view_bp.route('/design')
def design():
    return render_template('design.html')