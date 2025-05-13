from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
import pymysql
from config import Config
from datetime import datetime
import re

# 인증 블루프린트 정의
auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지"""
    if 'user_id' in session:
        return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
    
    # POST 요청 처리 (로그인 폼 제출)
    if request.method == 'POST':
        username = request.form.get('user_id')
        password = request.form.get('user_pw')
        remember = request.form.get('remember') == 'on'
        
        print(f"[로그인 시도] 사용자: {username}")  # 로그인 시도 로그
        
        # 입력값 검증
        if not username or not password:
            print("[로그인 실패] 아이디 또는 비밀번호 미입력")  # 실패 로그
            return jsonify({
                'success': False,
                'message': '아이디와 비밀번호를 모두 입력해주세요.'
            })
        
        # DB 연결
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
                # 사용자 조회
                sql = "SELECT * FROM USERS WHERE USER_ID = %s"
                cur.execute(sql, (username,))
                user = cur.fetchone()
                
                if user and bcrypt.check_password_hash(user['PASSWORD_HASH'], password):
                    # 세션에 사용자 정보 저장
                    session['user_id'] = user['USER_SEQ']
                    session['username'] = user['USER_ID']
                    session['logged_in'] = True
                    
                    print(f"[로그인 성공] 사용자: {username}")  # 성공 로그
                    next_page = request.args.get('next')
                    return jsonify({
                        'success': True,
                        'redirect': next_page if next_page else url_for('main.dashboard')
                    })
                else:
                    print(f"[로그인 실패] 사용자: {username} - 아이디/비밀번호 불일치")  # 실패 로그
                    return jsonify({
                        'success': False,
                        'message': '아이디와 비밀번호를 확인해주세요.'
                    })
        except Exception as e:
            print(f"[로그인 오류] 사용자: {username} - {str(e)}")  # 오류 로그
            return jsonify({
                'success': False,
                'message': f'로그인 중 오류가 발생했습니다: {str(e)}'
            })
        finally:
            if conn:
                conn.close()
            
    return render_template('auth/login.html', title='mindLog - 로그인')

@auth_bp.route('/join', methods=['GET'])
def join():
    return render_template('auth/join.html', title='회원가입')

@auth_bp.route('/register', methods=['POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    birth_date = request.form.get('birth_date')
    region = request.form.get('region')
    security_question = request.form.get('security_question')
    security_answer = request.form.get('security_answer')

    # 필수값 체크
    if not all([user_id, password, nickname, birth_date, region, security_question, security_answer]):
        flash('모든 항목을 입력해주세요.', 'danger')
        return render_template('auth/join.html', title='회원가입')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
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
        with conn.cursor() as cur:
            sql = "SELECT * FROM USERS WHERE USER_ID = %s"
            cur.execute(sql, (user_id,))
            if cur.fetchone():
                flash('이미 사용 중인 아이디입니다.', 'danger')
                return render_template('auth/join.html', title='회원가입')
            sql = """
            INSERT INTO USERS (USER_ID, PASSWORD_HASH, NICKNAME, BIRTH_DATE, REGION, SECURITY_QUESTION, SECURITY_ANSWER)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (user_id, hashed_password, nickname, birth_date, region, security_question, security_answer))
            conn.commit()
            flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
            return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f'회원가입 중 오류가 발생했습니다: {e}', 'danger')
        return render_template('auth/join.html', title='회원가입')
    finally:
        if conn:
            conn.close()

@auth_bp.route('/logout')
def logout():
    """로그아웃 처리"""
    session.clear()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """회원정보 수정 페이지"""
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
    
    # 사용자 정보 조회
    conn = None
    user_data = None
    
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
            sql = "SELECT * FROM USERS WHERE id = %s"
            cur.execute(sql, (session['user_id'],))
            user_data = cur.fetchone()
            
            if not user_data:
                flash('사용자 정보를 찾을 수 없습니다.', 'danger')
                return redirect(url_for('main.dashboard'))
                
            # POST 요청 처리 (회원정보 수정)
            if request.method == 'POST':
                nickname = request.form.get('nickname')
                current_password = request.form.get('current_password')
                new_password = request.form.get('password')
                
                # 닉네임 변경
                if nickname and nickname != user_data['nickname']:
                    update_sql = "UPDATE USERS SET nickname = %s WHERE id = %s"
                    cur.execute(update_sql, (nickname, session['user_id']))
                    conn.commit()
                    flash('닉네임이 변경되었습니다.', 'success')
                
                # 비밀번호 변경
                if current_password and new_password:
                    if not bcrypt.check_password_hash(user_data['password_hash'], current_password):
                        flash('현재 비밀번호가 일치하지 않습니다.', 'danger')
                    else:
                        # 비밀번호 유효성 검사
                        if len(new_password) < 8 or not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                            flash('새 비밀번호는 8자 이상이며, 영문/숫자/특수문자를 포함해야 합니다.', 'danger')
                        else:
                            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                            update_sql = "UPDATE USERS SET password_hash = %s WHERE id = %s"
                            cur.execute(update_sql, (hashed_password, session['user_id']))
                            conn.commit()
                            flash('비밀번호가 변경되었습니다.', 'success')
                
                # 수정된 정보로 업데이트
                sql = "SELECT * FROM USERS WHERE id = %s"
                cur.execute(sql, (session['user_id'],))
                user_data = cur.fetchone()
    except Exception as e:
        flash(f'오류가 발생했습니다: {e}', 'danger')
    finally:
        if conn:
            conn.close()
    
    return render_template('auth/update.html', title='mindLog - 회원정보', user=user_data)

@auth_bp.route('/delete', methods=['GET', 'POST'])
def delete_account():
    """회원탈퇴 페이지"""
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
    
    # POST 요청 처리 (회원탈퇴)
    if request.method == 'POST':
        password = request.form.get('pw')
        reason = request.form.get('reason')
        agree = request.form.get('check') == 'on'
        
        if not password or not reason or not agree:
            flash('모든 항목을 입력하고 동의해주세요.', 'danger')
            return render_template('auth/delete.html', title='mindLog - 회원탈퇴')
        
        # DB 연결
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
                # 사용자 조회 및 비밀번호 확인
                sql = "SELECT * FROM USERS WHERE id = %s"
                cur.execute(sql, (session['user_id'],))
                user = cur.fetchone()
                
                if not user or not bcrypt.check_password_hash(user['password_hash'], password):
                    flash('비밀번호가 일치하지 않습니다.', 'danger')
                    return render_template('auth/delete.html', title='mindLog - 회원탈퇴')
                
                # 탈퇴 사유 저장
                sql = "INSERT INTO withdrawal_reasons (user_id, reason, withdrawn_at) VALUES (%s, %s, %s)"
                cur.execute(sql, (session['user_id'], reason, datetime.now()))
                
                # 사용자 정보 삭제 (또는 비활성화)
                sql = "UPDATE USERS SET is_active = 0, withdrawn_at = %s WHERE id = %s"
                cur.execute(sql, (datetime.now(), session['user_id']))
                conn.commit()
                
                # 세션 초기화
                session.clear()
                
                flash('회원탈퇴가 완료되었습니다. 그동안 이용해주셔서 감사합니다.', 'info')
                return redirect(url_for('main.index'))
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'danger')
        finally:
            if conn:
                conn.close()
    
    return render_template('auth/delete.html', title='mindLog - 회원탈퇴')

@auth_bp.route('/find-password', methods=['GET'])
def find_password():
    return render_template('auth/find_password.html', title='mindLog - 비밀번호 찾기')

@auth_bp.route('/find-password/question', methods=['POST'])
def get_security_question():
    user_id = request.json.get('user_id')
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
            sql = "SELECT SECURITY_QUESTION FROM USERS WHERE USER_ID = %s"
            cur.execute(sql, (user_id,))
            user = cur.fetchone()
            if user:
                return jsonify({'success': True, 'question': user['SECURITY_QUESTION']})
            else:
                return jsonify({'success': False, 'message': '존재하지 않는 아이디입니다.'})
    finally:
        if conn:
            conn.close()

@auth_bp.route('/find-password/verify', methods=['POST'])
def verify_security_answer():
    user_id = request.json.get('user_id')
    answer = request.json.get('answer')
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
            sql = "SELECT SECURITY_ANSWER FROM USERS WHERE USER_ID = %s"
            cur.execute(sql, (user_id,))
            user = cur.fetchone()
            if user and user['SECURITY_ANSWER'] == answer:
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': '답변이 일치하지 않습니다.'})
    finally:
        if conn:
            conn.close()

@auth_bp.route('/find-password/reset', methods=['POST'])
def reset_password():
    user_id = request.json.get('user_id')
    new_password = request.json.get('new_password')
    bcrypt = Bcrypt()
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
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
        with conn.cursor() as cur:
            sql = "UPDATE USERS SET PASSWORD_HASH = %s WHERE USER_ID = %s"
            cur.execute(sql, (hashed_password, user_id))
            conn.commit()
            return jsonify({'success': True})
    finally:
        if conn:
            conn.close()

@auth_bp.route('/check-id', methods=['POST'])
def check_id():
    data = request.get_json()
    user_id = data.get('user_id')
    exists = False

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
        with conn.cursor() as cur:
            sql = "SELECT 1 FROM USERS WHERE USER_ID = %s"
            cur.execute(sql, (user_id,))
            if cur.fetchone():
                exists = True
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)})
    finally:
        if conn:
            conn.close()
    return jsonify({'exists': exists})