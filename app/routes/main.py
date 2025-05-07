from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import current_user, login_required
import pymysql
from config import Config

# 메인 블루프린트 정의
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """메인 홈페이지 라우트"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('main.html', title='mindLog - 당신의 마음 건강을 위한 공간')

@main_bp.route('/dashboard')
def dashboard():
    """사용자 대시보드 - 로그인 필요"""
    if 'user_id' not in session:
        flash('대시보드에 접근하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
    
    # 센터 정보 가져오기
    centers = get_nearby_centers(session.get('user_location', '서울'))
    
    # 사용자 정보 가져오기
    user_info = get_user_info(session.get('user_id'))
    
    return render_template(
        'main.html', 
        title='mindLog - 내 대시보드',
        user=user_info,
        centers=centers
    )

@main_bp.route('/about')
def about():
    """서비스 소개 페이지"""
    return render_template('about.html', title='mindLog - 서비스 소개')

@main_bp.route('/contact')
def contact():
    """문의하기 페이지"""
    return render_template('contact.html', title='mindLog - 문의하기')

@main_bp.route('/privacy')
def privacy():
    """개인정보 처리방침 페이지"""
    return render_template('privacy.html', title='mindLog - 개인정보 처리방침')

@main_bp.route('/terms')
def terms():
    """이용약관 페이지"""
    return render_template('terms.html', title='mindLog - 이용약관')

@main_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """사용자 알림 가져오기"""
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    
    # 알림 가져오기 (예시 데이터)
    notifications = [
        {"title": "우울증 자가진단 결과", "message": "지난 자가진단 결과가 저장되었습니다.", "date": "2023-05-01"},
        {"title": "챗봇 알림", "message": "새로운 대화를 시작해보세요.", "date": "2023-05-02"}
    ]
    
    return jsonify({"notifications": notifications})

# 유틸리티 함수
def get_nearby_centers(location):
    """위치 기반으로 주변 상담센터 정보 가져오기"""
    # 실제 구현에서는 데이터베이스에서 가져와야 함
    # 예시 데이터
    centers = [
        {
            "name": "마음돌봄 심리상담센터",
            "type": "심리상담센터",
            "address": f"{location} 남구 봉선로 123",
            "phone": "062-123-4567",
            "distance": "1.5km"
        },
        {
            "name": "희망 심리상담소",
            "type": "심리상담센터",
            "address": f"{location} 남구 방림로 789",
            "phone": "062-555-6789",
            "distance": "3.1km"
        }
    ]
    return centers

def get_user_info(user_id):
    """사용자 정보 가져오기"""
    conn = None
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            db=Config.DB_NAME,
            charset='utf8mb4'
        )
        
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            # 사용자 정보 조회
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            
            if user:
                # 가입일 계산
                import datetime
                join_date = user.get('created_at')
                today = datetime.datetime.now()
                days_joined = (today - join_date).days if join_date else 0
                
                return {
                    "id": user.get('id'),
                    "username": user.get('username'),
                    "nickname": user.get('nickname') or user.get('username'),
                    "days_joined": days_joined
                }
            
            return {"username": "사용자", "days_joined": 0}
    except Exception as e:
        print(f"사용자 정보 조회 오류: {e}")
        return {"username": "사용자", "days_joined": 0}
    finally:
        if conn:
            conn.close()