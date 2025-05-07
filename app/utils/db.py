import pymysql
from flask import current_app, g
import traceback

def get_db():
    """데이터베이스 연결 가져오기"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['DB_HOST'],
            port=current_app.config['DB_PORT'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            db=current_app.config['DB_NAME'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    """데이터베이스 연결 닫기"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Flask 앱에 데이터베이스 유틸리티 등록"""
    app.teardown_appcontext(close_db)

def init_db(app):
    """데이터베이스 연결 확인"""
    with app.app_context():
        conn = get_db()
        try:
            with conn.cursor() as cur:
                # 기존 테이블이 있는지 확인
                cur.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name IN ('USERS', 'SELFDIAGNOSIS', 'COUNSELINGCENTERS', 'APPOINTMENTS', 'CHATMESSAGES')
                """, (current_app.config['DB_NAME'],))
                
                result = cur.fetchone()
                if result and result['count'] == 5:
                    app.logger.info("데이터베이스 테이블이 모두 존재합니다.")
                else:
                    app.logger.warning("일부 테이블이 누락되었습니다. 시스템 관리자에게 문의하세요.")
                    
        except Exception as e:
            app.logger.error(f"데이터베이스 연결 확인 오류: {e}")
            app.logger.debug(traceback.format_exc())