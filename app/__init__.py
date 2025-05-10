from flask import Flask, render_template
from flask_session import Session
from flask_login import LoginManager
from config import Config
import pymysql
import os
from app.routes import auth_bp, main_bp, counseling_bp, diagnosis_bp, chatbot_bp  # 필요한 블루프린트 모두 import

def create_app():
    """
    Flask 애플리케이션을 생성하고 설정합니다.
    """
    # Flask 애플리케이션 인스턴스 생성
    app = Flask(__name__)
    
    # 설정 로드
    app.config.from_object(Config)
    #jinja loop컨트롤러 break나 continue 사용가능
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    # 세션 설정 (Config에서 가져옴)
    Session(app)
    
    # Flask-Login 설정
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요한 페이지입니다.'
    login_manager.login_message_category = 'error'
    
    # 사용자 로더 함수 정의
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.users import User
        # 데이터베이스에서 사용자 정보 로드
        conn = Config.get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM USERS WHERE USER_SEQ = %s"
                cursor.execute(sql, (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(user_data)
                return None
        finally:
            conn.close()
    
    # 블루프린트 등록
    # 블루프린트 등록
    app.register_blueprint(main_bp)  # 메인 페이지
    app.register_blueprint(auth_bp, url_prefix='/auth')  # 인증 관련
    app.register_blueprint(diagnosis_bp, url_prefix='/diagnosis')  # 자가진단
    app.register_blueprint(counseling_bp, url_prefix='/counseling')  # 상담센터
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')  # 챗봇
    
    # 에러 핸들러 등록
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """
    Flask 애플리케이션에 에러 핸들러를 등록합니다.
    
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500