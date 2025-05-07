import os
from app import create_app
from config import config

# 개발 환경 설정 사용
app = create_app(config['development'])

if __name__ == '__main__':
    # 기본 포트와 호스트 설정
    host = '0.0.0.0'
    port = 5000
    
    # 애플리케이션 실행
    app.run(host=host, port=port, debug=True)