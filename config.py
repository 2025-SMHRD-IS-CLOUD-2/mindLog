import os
from datetime import timedelta
import pymysql

class Config:
    # 데이터베이스 연결 정보
    DB_HOST = 'project-db-cgi.smhrd.com'
    DB_PORT = 3307
    DB_USER = 'CGI_24IS_CLOUD_P2_1'
    DB_PASSWORD = 'smhrd1'
    DB_NAME = 'CGI_24IS_CLOUD_P2_1'
    
    # Flask 애플리케이션 설정
    SECRET_KEY = 'mindLog'
    
    # 세션 설정
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # SQLAlchemy 설정
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 파일 업로드 설정
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 최대 16MB 업로드
    
    # CSRF 보호
    WTF_CSRF_ENABLED = True
    
    # 개발 환경 설정
    DEBUG = True

    @staticmethod
    def get_db_connection():
        """
        데이터베이스 연결 객체를 반환합니다.
        """
        return pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            db=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )