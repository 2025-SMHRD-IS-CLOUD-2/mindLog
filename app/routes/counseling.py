from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
import pymysql
from datetime import datetime,timedelta

import pymysql.cursors
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
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            today = datetime.now()
            sql = today.strftime(f"""SELECT C.CENTER_SEQ,NAME,ADDRESS,CONTACT,APPOINTMENT_SEQ,
            APPOINTMENT_DATE,APPOINTMENT_TIME
            FROM APPOINTMENTS AS  A INNER JOIN COUNSELINGCENTERS AS C
            WHERE USER_SEQ =  '{session["user_id"]}'
            AND A.CENTER_SEQ = C.CENTER_SEQ
            AND APPOINTMENT_DATE = '%Y-%m-%d'
            ORDER BY APPOINTMENT_TIME ASC""")
            cursor.execute(sql)
            result = cursor.fetchall()
            conn.close()
            for row in result:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        row[key] = str(value)
        return render_template('counseling/schedule.html',result = result,today = today)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@counseling_bp.route('/get_schedule',methods = ['POST'])
def get_data():
    date = request.get_json()
    year = date.get("year")
    month = date.get("month")
    day = date.get("day")
    sc = datetime(int(year),int(month),int(day))
    try:
        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = sc.strftime(f"""SELECT C.CENTER_SEQ,NAME,ADDRESS,CONTACT,APPOINTMENT_SEQ,
            APPOINTMENT_DATE,APPOINTMENT_TIME
            FROM APPOINTMENTS AS  A INNER JOIN COUNSELINGCENTERS AS C
            WHERE USER_SEQ =  '{session["user_id"]}'
            AND A.CENTER_SEQ = C.CENTER_SEQ
            AND APPOINTMENT_DATE = '%Y-%m-%d'
            ORDER BY APPOINTMENT_TIME ASC""")
            cursor.execute(sql)
            result = cursor.fetchall()
            conn.close()
            for row in result:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        row[key] = str(value)
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

@counseling_bp.route('/appointment', methods = ['GET'])
def appointment():
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('상담 예약을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    # 상담센터 정보 조회
    name = request.args.get("name")
    address = request.args.get("address")
    phone = request.args.get("phone")
    today = datetime.now()
    conn = get_db_connection()
    today = today.strftime("%Y-%m-%d")
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = f"SELECT CENTER_SEQ,NAME,ADDRESS,CONTACT FROM COUNSELINGCENTERS WHERE NAME = '{name}' AND ADDRESS = '{address}' AND contact = '{phone}'"
            cursor.execute(sql)
            center = cursor.fetchone()
            sql = f"""
            SELECT APPOINTMENT_TIME
            FROM APPOINTMENTS
            WHERE CENTER_SEQ = (SELECT CENTER_SEQ FROM COUNSELINGCENTERS WHERE NAME = '{name}' AND ADDRESS = '{address}' AND contact = '{phone}')
            AND APPOINTMENT_DATE = '{today}'"""
            cursor.execute(sql)
            appointment = cursor.fetchall()
            for row in appointment:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        row[key] = int(str(value).replace(":00:00",""))

    finally:
        conn.close()
    return render_template('counseling/appointment.html', center = center,appointment = appointment,today = today)

@counseling_bp.route("/get_time",methods = ["POST"])
def getTime():
    centerInfo = request.get_json()
    selectDay = centerInfo.get("select_day")
    centerSeq = centerInfo.get("center_seq")

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = f""" SELECT APPOINTMENT_TIME 
            FROM APPOINTMENTS 
            WHERE APPOINTMENT_DATE = '{selectDay}' 
            AND CENTER_SEQ =  {centerSeq}
            ORDER BY APPOINTMENT_TIME ASC"""
            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                for key, value in row.items():
                    if isinstance(value, timedelta):
                        row[key] = str(value).replace(":00:00","")           
    finally:
        conn.close()
    return jsonify(result)
        
    

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

@counseling_bp.route('/update-appointment', methods=['GET', 'POST'])
def update_appointment():
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('예약 수정을 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    
    data = request.get_json()
    date = data.get("date")
    time = data.get("time")
    seq = data.get("seq")
    # 예약 정보 업데이트
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """UPDATE APPOINTMENTS 
                    SET APPOINTMENT_DATE = %s, APPOINTMENT_TIME = %s,
                    WHERE APPOINTMENT_SEQ = %s"""
            cursor.execute(sql, (date, time,seq))
            conn.commit()
            
    except Exception as e:
        conn.rollback()
        flash(f'예약 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    finally:
        conn.close()
    return "예약 변경이 완료 되었습니다."

@counseling_bp.route('/cancel-appointment', methods=['GET'])
def cancel_appointment():
    # 로그인 상태 확인
    if 'user_id' not in session:
        flash('예약 취소를 위해 로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))
    appointmentSeq = request.args.get('appointmentSeq',type = int)
    # 예약 취소
    conn = get_db_connection()
    print(appointmentSeq,session["user_id"])
    try:
        with conn.cursor() as cursor:
            
            # 예약 삭제
            sql = "DELETE FROM APPOINTMENTS WHERE APPOINTMENT_SEQ = %s AND USER_SEQ = %s"
            cursor.execute(sql, (appointmentSeq, int(session['user_id'])))
            conn.commit()
            
            flash('예약이 취소되었습니다.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'예약 취소 중 오류가 발생했습니다: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('counseling.schedule'))

@counseling_bp.route('/api/counseling_centers')
def get_counseling_centers():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute('SELECT CENTER_SEQ, NAME, LATITUDE, LONGITUDE, ADDRESS, CONTACT FROM COUNSELINGCENTERS')
            centers = cursor.fetchall()  # 실제 데이터 fetch
    finally:
        conn.close()
    return jsonify(centers)

@counseling_bp.route('/insert_appointment',methods = ["POST"])
def insert_appointment():
    conn = get_db_connection()
    data = request.get_json()
    date = str(data["date"])
    time = str(data["time"])
    center = int(data["centerSeq"])
    print(session)
    print(date,time,center,session["user_id"])
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"""
        INSERT INTO APPOINTMENTS(USER_SEQ,CENTER_SEQ,
                        APPOINTMENT_DATE,APPOINTMENT_TIME,
                        STATUS) VALUES({session["user_id"]},{center},'{date}','{time}','confirmed')
        """)
            conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f'예약 중 오류가 발생했습니다: {str(e)}', 'error')

    finally:
        conn.close()
        return jsonify({"url":url_for("counseling.success")})
    

@counseling_bp.route("/success")
def success():
    return render_template("counseling/success.html")



