from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
import pymysql
from datetime import datetime,timedelta
from config import Config

counseling_bp = Blueprint('counseling', __name__)

# 데이터베이스 연결 함수
def get_db_connection():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        db=Config.DB_NAME,
        charset='utf8mb4'
    )
    return conn
@counseling_bp.route('/schedule')
def schedule():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    session
    sql = f"""SELECT * 
    FROM APPOINTMENTS 
    WHERE USER_SEQ = (SELECT USER_SEQ FROM USERS WHERE USER_ID = 'TEST1')""" #{session.get('id')}
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close();
    return render_template('counseling/schedule.html',result = result)

@counseling_bp.route('/get_schedule',methods = ['POST'])
def get_data():
    try:
        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM APPOINTMENTS WHERE USER_SEQ = 1"
            cursor.execute(sql)
            result = cursor.fetchall()  # [{'id': 1, 'name': 'Alice'}, ...]
            for row in result:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        row[key] = str(value)
            print(result)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@counseling_bp.route('/centers')
def centers():
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('상담센터 검색을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 사용자 지역 정보 가져오기
    user_region = session.get('region', '')
    
    # 상담센터 목록 조회
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            if user_region:
                # 사용자 지역 기반 상담센터 검색
                sql = """SELECT * FROM COUNSELINGCENTERS 
                        WHERE ADDRESS LIKE %s 
                        ORDER BY NAME"""
                cursor.execute(sql, (f'%{user_region}%',))
            else:
                # 전체 상담센터 조회
                sql = "SELECT * FROM COUNSELINGCENTERS ORDER BY NAME"
                cursor.execute(sql)
            
            centers = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('counseling/centers.html', 
                          centers=centers, 
                          user_region=user_region)

@counseling_bp.route('/search', methods=['GET'])
def search():
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('상담센터 검색을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 검색어 가져오기
    keyword = request.args.get('keyword', '')
    region = request.args.get('region', '')
    
    # 검색 조건 구성
    conditions = []
    params = []
    
    if keyword:
        conditions.append("NAME LIKE %s")
        params.append(f'%{keyword}%')
    
    if region:
        conditions.append("ADDRESS LIKE %s")
        params.append(f'%{region}%')
    
    # 상담센터 검색
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            if conditions:
                sql = f"""SELECT * FROM COUNSELINGCENTERS 
                        WHERE {' AND '.join(conditions)} 
                        ORDER BY NAME"""
                cursor.execute(sql, params)
            else:
                sql = "SELECT * FROM COUNSELINGCENTERS ORDER BY NAME"
                cursor.execute(sql)
            
            centers = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('counseling/search_results.html', 
                          centers=centers, 
                          keyword=keyword, 
                          region=region)

@counseling_bp.route('/center/<int:center_id>')
def center_detail(center_id):
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('상담센터 정보 확인을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 상담센터 상세 정보 조회
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM COUNSELINGCENTERS WHERE CENTER_SEQ = %s"
            cursor.execute(sql, (center_id,))
            center = cursor.fetchone()
            
            if not center:
                flash('존재하지 않는 상담센터입니다.', 'error')
                return redirect(url_for('counseling.centers'))
    finally:
        conn.close()
    
    return render_template('counseling/center_detail.html', center=center)

@counseling_bp.route('/appointment/<int:center_id>', methods=['GET', 'POST'])
def appointment(center_id):
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('상담 예약을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 상담센터 정보 조회
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM COUNSELINGCENTERS WHERE CENTER_SEQ = %s"
            cursor.execute(sql, (center_id,))
            center = cursor.fetchone()
            
            if not center:
                flash('존재하지 않는 상담센터입니다.', 'error')
                return redirect(url_for('counseling.centers'))
    finally:
        conn.close()
    
    if request.method == 'POST':
        # 예약 정보 가져오기
        date = request.form.get('appointment_date')
        time = request.form.get('appointment_time')
        
        if not date or not time:
            flash('날짜와 시간을 모두 선택해주세요.', 'error')
            return render_template('counseling/appointment.html', center=center)
        
        # 예약 정보 저장
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """INSERT INTO APPOINTMENTS 
                        (USER_SEQ, CENTER_SEQ, APPOINTMENT_DATE, APPOINTMENT_TIME, STATUS) 
                        VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (session['user_seq'], center_id, date, time, 'pending'))
                conn.commit()
                
                flash('상담 예약이 완료되었습니다.', 'success')
                return redirect(url_for('counseling.my_appointments'))
        except Exception as e:
            conn.rollback()
            flash(f'예약 중 오류가 발생했습니다: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('counseling/appointment.html', center=center)

@counseling_bp.route('/my-appointments')
def my_appointments():
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('예약 내역 확인을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 사용자 예약 내역 조회
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """SELECT a.*, c.NAME as CENTER_NAME, c.ADDRESS as CENTER_ADDRESS 
                    FROM APPOINTMENTS a
                    JOIN COUNSELINGCENTERS c ON a.CENTER_SEQ = c.CENTER_SEQ
                    WHERE a.USER_SEQ = %s
                    ORDER BY a.APPOINTMENT_DATE, a.APPOINTMENT_TIME"""
            cursor.execute(sql, (session['user_seq'],))
            appointments = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('counseling/my_appointments.html', appointments=appointments)

@counseling_bp.route('/update-appointment/<int:appointment_id>', methods=['GET', 'POST'])
def update_appointment(appointment_id):
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('예약 수정을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 예약 정보 조회
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """SELECT a.*, c.NAME as CENTER_NAME, c.CENTER_SEQ
                    FROM APPOINTMENTS a
                    JOIN COUNSELINGCENTERS c ON a.CENTER_SEQ = c.CENTER_SEQ
                    WHERE a.APPOINTMENT_SEQ = %s AND a.USER_SEQ = %s"""
            cursor.execute(sql, (appointment_id, session['user_seq']))
            appointment = cursor.fetchone()
            
            if not appointment:
                flash('존재하지 않는 예약이거나 권한이 없습니다.', 'error')
                return redirect(url_for('counseling.my_appointments'))
            
            # 상담센터 정보 조회
            sql = "SELECT * FROM COUNSELINGCENTERS WHERE CENTER_SEQ = %s"
            cursor.execute(sql, (appointment['CENTER_SEQ'],))
            center = cursor.fetchone()
    finally:
        conn.close()
    
    if request.method == 'POST':
        # 수정된 예약 정보 가져오기
        date = request.form.get('appointment_date')
        time = request.form.get('appointment_time')
        
        if not date or not time:
            flash('날짜와 시간을 모두 선택해주세요.', 'error')
            return render_template('counseling/update_appointment.html', 
                                  appointment=appointment,
                                  center=center)
        
        # 예약 정보 업데이트
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """UPDATE APPOINTMENTS 
                        SET APPOINTMENT_DATE = %s, APPOINTMENT_TIME = %s, STATUS = %s
                        WHERE APPOINTMENT_SEQ = %s AND USER_SEQ = %s"""
                cursor.execute(sql, (date, time, 'pending', appointment_id, session['user_seq']))
                conn.commit()
                
                flash('예약이 성공적으로 수정되었습니다.', 'success')
                return redirect(url_for('counseling.my_appointments'))
        except Exception as e:
            conn.rollback()
            flash(f'예약 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('counseling/update_appointment.html', 
                          appointment=appointment,
                          center=center)

@counseling_bp.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('예약 취소를 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 예약 취소
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 사용자의 예약인지 확인
            sql = """SELECT COUNT(*) FROM APPOINTMENTS 
                    WHERE APPOINTMENT_SEQ = %s AND USER_SEQ = %s"""
            cursor.execute(sql, (appointment_id, session['user_seq']))
            if cursor.fetchone()[0] == 0:
                flash('존재하지 않는 예약이거나 권한이 없습니다.', 'error')
                return redirect(url_for('counseling.my_appointments'))
            
            # 예약 삭제
            sql = "DELETE FROM APPOINTMENTS WHERE APPOINTMENT_SEQ = %s AND USER_SEQ = %s"
            cursor.execute(sql, (appointment_id, session['user_seq']))
            conn.commit()
            
            flash('예약이 취소되었습니다.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'예약 취소 중 오류가 발생했습니다: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('counseling.my_appointments'))