# 라우트 모듈 임포트
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.diagnosis import diagnosis_bp
from app.routes.counseling import counseling_bp
from app.routes.chatbot import chatbot_bp

# 블루프린트 등록 함수
def register_blueprints(app):
    """
    Flask 애플리케이션에 모든 블루프린트를 등록합니다.
    
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(diagnosis_bp, url_prefix='/diagnosis')
    app.register_blueprint(counseling_bp, url_prefix='/counseling')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')