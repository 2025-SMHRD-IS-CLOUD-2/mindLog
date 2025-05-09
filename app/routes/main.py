from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import current_user, login_required
import pymysql
from config import Config
import datetime

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
    
    # 사용자 정보 가져오기
    user_info = get_user_info(session.get('user_id'))
    region = user_info.get('region', '서울')
    # 센터 정보 가져오기
    centers = get_nearby_centers(region)
    
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
def get_nearby_centers(region):
    """위치 기반으로 주변 상담센터 정보 가져오기"""
    # region이 없으면 '서울'로 기본값 설정
    if not region:
        region = '서울'

    conn = None
    centers = []
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
            sql = "SELECT * FROM COUNSELINGCENTERS WHERE ADDRESS LIKE %s"
            cur.execute(sql, (f"%{region}%",))
            results = cur.fetchall()
            for row in results:
                centers.append({
                    "name": row['NAME'],
                    "type": "청소년상담복지센터",
                    "address": row['ADDRESS'],
                    "phone": row['CONTACT'],
                    "distance": ""  # 거리 계산 불가, 빈 값
                })
    except Exception as e:
        print(f"센터 정보 조회 오류: {e}")
    finally:
        if conn:
            conn.close()
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
            cur.execute("SELECT * FROM USERS WHERE USER_SEQ = %s", (user_id,))
            user = cur.fetchone()
            
            if user:
                # 가입일 계산
                today = datetime.datetime.now().date()
                join_date = user.get('CREATED_AT')
                days_joined = 0
                if join_date:
                    if isinstance(join_date, str):
                        join_date = datetime.datetime.strptime(join_date, '%Y-%m-%d %H:%M:%S').date()
                    else:
                        join_date = join_date.date()
                    days_joined = (today - join_date).days
                return {
                    "id": user.get('USER_SEQ'),
                    "username": user.get('USER_ID'),
                    "nickname": user.get('NICKNAME') or user.get('USER_ID'),
                    "region": user.get('REGION'),
                    "days_joined": days_joined
                }
            
            return {"username": "사용자", "days_joined": 0}
    except Exception as e:
        print(f"사용자 정보 조회 오류: {e}")
        return {"username": "사용자", "days_joined": 0}
    finally:
        if conn:
            conn.close()