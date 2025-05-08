from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/check-id', methods=['POST'])
def check_id():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': '아이디를 입력해주세요.'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM USERS WHERE USER_ID = ?', (user_id,))
        count = cursor.fetchone()[0]
        
        return jsonify({'exists': count > 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@auth.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        name = request.form['name']
        birth = request.form['birth']
        gender = request.form['gender']
        
        # 비밀번호 확인
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.')
            return redirect(url_for('auth.join'))
        
        # 비밀번호 유효성 검사
        if len(password) < 8 or not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password) or not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            flash('비밀번호는 8자 이상, 특수기호를 포함하고, 영어와 숫자를 조합해야 합니다.')
            return redirect(url_for('auth.join'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 아이디 중복 검사
            cursor.execute('SELECT COUNT(*) FROM USERS WHERE USER_ID = ?', (user_id,))
            if cursor.fetchone()[0] > 0:
                flash('이미 사용 중인 아이디입니다.')
                return redirect(url_for('auth.join'))
            
            # 비밀번호 해시화
            hashed_password = generate_password_hash(password)
            
            # 사용자 정보 저장
            cursor.execute('''
                INSERT INTO USERS (USER_ID, PASSWORD, NAME, BIRTH, GENDER)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, hashed_password, name, birth, gender))
            
            conn.commit()
            flash('회원가입이 완료되었습니다.')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            conn.rollback()
            flash('회원가입 중 오류가 발생했습니다.')
            return redirect(url_for('auth.join'))
            
        finally:
            cursor.close()
            conn.close()
    
    return render_template('join.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM USERS WHERE USER_ID = ?', (user_id,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['PASSWORD'], password):
                session['user_id'] = user['USER_ID']
                session['name'] = user['NAME']
                flash('로그인되었습니다.')
                return redirect(url_for('main.index'))
            else:
                flash('아이디 또는 비밀번호가 올바르지 않습니다.')
                return redirect(url_for('auth.login'))
                
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('main.index')) 