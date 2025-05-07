import os
from dotenv import load_dotenv

# 환경변수를 사용하는 경우를 위해 load_dotenv() 유지
load_dotenv()

class Config:
    # SECRET_KEY 설정
    SECRET_KEY = 'mindLog'
    
    # 데이터베이스 설정 - 직접 하드코딩
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://CGI_24IS_CLOUD_P2_1:smhrd1@project-db-cgi.smhrd.com:3307/CGI_24IS_CLOUD_P2_1?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 앱 설정
    DEBUG = True
    TESTING = False
    
    # 세션 설정
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30분
    
    # 업로드 설정
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 최대 업로드 크기 16MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    
    # 위험 키워드 목록 (챗봇에서 위험 감지에 사용)
    RISK_KEYWORDS = [
        '자살', '자해', '죽고 싶다', '목숨', '생을 마감', 
        '살기 싫다', '죽을 것 같다', '약을 먹을 것이다',
        '더 이상 살고 싶지 않다', '사라지고 싶다'
    ]

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'mindLog'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://CGI_24IS_CLOUD_P2_1:smhrd1@project-db-cgi.smhrd.com:3307/CGI_24IS_CLOUD_P2_1?charset=utf8mb4'

# 환경에 따라 적절한 설정 선택
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}