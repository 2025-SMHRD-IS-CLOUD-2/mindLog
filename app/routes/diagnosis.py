from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import pymysql
from datetime import datetime
import json
from config import Config

# 자가진단 블루프린트 정의
diagnosis_bp = Blueprint('diagnosis', __name__)

# 설문지 정의 - PHQ-9
PHQ9_QUESTIONS = [
    "기분이 가라앉거나, 우울하거나, 희망이 없다고 느꼈다.",
    "평소 하던 일에 대한 흥미가 없어지거나 즐거움을 느끼지 못했다.",
    "잠들기 어렵거나 자주 깨어남, 혹은 너무 많이 잤다.",
    "피곤하다고 느끼거나 기운이 거의 없었다.",
    "식욕 저하 혹은 과식하는 경향이 있었다.",
    "자신을 부정적으로 봤다. 혹은 자신이 실패자라고 느끼거나 자신과 가족을 실망시켰다고 느꼈다.",
    "신문을 읽거나 TV를 보는 것과 같은 일에 집중하기 어려웠다.",
    "다른 사람들이 눈치 챌 정도로 너무 느리게 움직이거나 말을 했다. 또는 반대로 평소보다 많이 움직여서 너무 안절부절 못하거나 들떠 있었다.",
    "자신이 죽는 것이 더 낫다고 생각하거나 어떤 식으로든 자신을 해칠 것이라고 생각했다."
]

# 설문지 정의 - CES-D
CESD_QUESTIONS = [
    "평소에는 아무렇지도 않던 일들이 괴롭고 귀찮게 느껴졌다.",
    "먹고 싶지 않았다; 입맛이 없었다.",
    "가족이나 친구가 도와주더라도 울적한 기분을 떨쳐버릴 수 없었다.",
    "다른 사람들만큼 능력이 있다고 느꼈다.",
    "무슨 일을 하든 정신을 집중하기가 힘들었다.",
    "우울했다.",
    "하는 일마다 힘들게 느껴졌다.",
    "미래에 대하여 희망적으로 느꼈다.",
    "내 인생은 실패작이라는 생각이 들었다.",
    "두려움을 느꼈다.",
    "잠을 설쳤다; 잠을 이루지 못했다.",
    "행복했다.",
    "평소보다 말을 적게 했다; 말수가 줄었다.",
    "세상에 홀로 있는 듯한 외로움을 느꼈다.",
    "사람들이 나에게 차갑게 대하는 것 같았다.",
    "생활이 즐거웠다.",
    "갑자기 울음이 나왔다.",
    "슬픔을 느꼈다.",
    "사람들이 나를 싫어하는 것 같았다.",
    "도무지 무엇을 시작할 기운이 나지 않았다."
]

# 설문지 정의 - CESD-10-D (CES-D의 축약형)
CESD10_QUESTIONS = [
    "비교적 잘 지냈다.",
    "상당히 우울했다.",
    "모든 일들이 힘겹게 느껴졌다.",
    "잠을 설쳤다(자는 중에 이루지 못했다).",
    "세상에 홀로 있는 듯한 외로움을 느꼈다.",
    "큰 불안 없이 생활했다.",
    "사람들이 나에게 친절하지 않은 것 같았다.",
    "기운이 솟았다.",
    "사람들이 나를 싫어하는 것 같았다.",
    "도무지 해낼 힘이 나질 않거나 의욕이 나지 않았다."
]

@diagnosis_bp.route('/')
def index():
    """자가진단 시작 페이지"""
    if 'user_id' not in session:
        flash('자가진단을 이용하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
        
    return render_template('diagnosis/index.html', title='mindLog - 자가진단 시작')

@diagnosis_bp.route('/info')
def info():
    """자가진단 정보 안내 페이지"""
    return render_template('diagnosis/info.html', title='mindLog - 자가진단 정보')

@diagnosis_bp.route('/phq9', methods=['GET', 'POST'])
def phq9():
    """PHQ-9 자가진단 페이지"""
    if 'user_id' not in session:
        flash('자가진단을 이용하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        # 사용자 응답 처리
        responses = []
        total_score = 0
        
        for i in range(1, 10):  # PHQ-9는 9개 문항
            answer = int(request.form.get(f'q{i}', 0))
            responses.append(answer)
            total_score += answer
        
        # 결과 해석
        result = {}
        if total_score <= 4:
            result['severity'] = '정상'
            result['description'] = '우울증이 없는 상태입니다.'
            result['recommendation'] = '현재 상태를 유지하세요.'
            result['risk_level'] = 'low'
        elif total_score <= 9:
            result['severity'] = '가벼운 우울증'
            result['description'] = '가벼운 우울 증상이 있습니다.'
            result['recommendation'] = '자가 관리와 정기적인 기분 체크를 권장합니다.'
            result['risk_level'] = 'low'
        elif total_score <= 14:
            result['severity'] = '중간 정도의 우울증'
            result['description'] = '중간 정도의 우울 증상이 있습니다.'
            result['recommendation'] = '전문가와 상담을 고려해보세요.'
            result['risk_level'] = 'medium'
        elif total_score <= 19:
            result['severity'] = '심한 우울증'
            result['description'] = '심한 우울 증상이 있습니다.'
            result['recommendation'] = '전문가의 도움을 받는 것이 좋습니다.'
            result['risk_level'] = 'high'
        else:
            result['severity'] = '심각한 우울증'
            result['description'] = '심각한 우울 증상이 있습니다.'
            result['recommendation'] = '즉시 전문가의 도움을 받으세요.'
            result['risk_level'] = 'high'
        
        # 9번 문항(자살 생각) 체크
        if responses[8] >= 1:
            result['warning'] = '자살 생각이 있는 것으로 보입니다. 즉시 전문가의 도움을 받으세요.'
            result['risk_level'] = 'high'
        
        # 결과 저장 (로그인한 경우만)
        if 'user_id' in session:
            save_diagnosis_result(
                session['user_id'], 
                'PHQ-9', 
                total_score, 
                responses, 
                result
            )
        
        # 세션에 결과 저장 (결과 페이지에서 사용)
        session['diagnosis_result'] = {
            'test_type': 'PHQ-9',
            'score': total_score,
            'responses': responses,
            'result': result,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return redirect(url_for('diagnosis.result'))
    
    # GET 요청 처리 (설문지 표시)
    return render_template('diagnosis/phq9.html', 
                          title='mindLog - PHQ-9 자가진단',
                          questions=PHQ9_QUESTIONS)

@diagnosis_bp.route('/cesd', methods=['GET', 'POST'])
def cesd():
    """CES-D 자가진단 페이지"""
    if 'user_id' not in session:
        flash('자가진단을 이용하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        # 사용자 응답 처리
        responses = []
        total_score = 0
        
        for i in range(1, 21):  # CES-D는 20개 문항
            answer = int(request.form.get(f'q{i}', 0))
            # 4, 8, 12, 16번 문항은 긍정 문항으로 역채점
            if i in [4, 8, 12, 16]:
                answer = 3 - answer  # 역채점 (0→3, 1→2, 2→1, 3→0)
            
            responses.append(answer)
            total_score += answer
        
        # 결과 해석
        result = {}
        if total_score < 16:
            result['severity'] = '정상'
            result['description'] = '우울증이 없는 상태입니다.'
            result['recommendation'] = '현재 상태를 유지하세요.'
            result['risk_level'] = 'low'
        elif total_score < 21:
            result['severity'] = '경도 우울증'
            result['description'] = '가벼운 우울 증상이 있습니다.'
            result['recommendation'] = '자가 관리와 정기적인 기분 체크를 권장합니다.'
            result['risk_level'] = 'low'
        elif total_score < 25:
            result['severity'] = '중등도 우울증'
            result['description'] = '중간 정도의 우울 증상이 있습니다.'
            result['recommendation'] = '전문가와 상담을 고려해보세요.'
            result['risk_level'] = 'medium'
        else:
            result['severity'] = '중증 우울증'
            result['description'] = '심한 우울 증상이 있습니다.'
            result['recommendation'] = '전문가의 도움을 받는 것이 좋습니다.'
            result['risk_level'] = 'high'
        
        # 결과 저장 (로그인한 경우만)
        if 'user_id' in session:
            save_diagnosis_result(
                session['user_id'], 
                'CES-D', 
                total_score, 
                responses, 
                result
            )
        
        # 세션에 결과 저장 (결과 페이지에서 사용)
        session['diagnosis_result'] = {
            'test_type': 'CES-D',
            'score': total_score,
            'responses': responses,
            'result': result,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return redirect(url_for('diagnosis.result'))
    
    # GET 요청 처리 (설문지 표시)
    return render_template('diagnosis/cesd.html', 
                          title='mindLog - CES-D 자가진단',
                          questions=CESD_QUESTIONS)

@diagnosis_bp.route('/cesd10', methods=['GET', 'POST'])
def cesd10():
    """CES-D-10 자가진단 페이지 (CES-D의 축약형)"""
    if 'user_id' not in session:
        flash('자가진단을 이용하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        # 사용자 응답 처리
        responses = []
        total_score = 0
        
        for i in range(1, 11):  # CES-D-10은 10개 문항
            answer = int(request.form.get(f'q{i}', 0))
            # 1, 6, 8번 문항은 긍정 문항으로 역채점
            if i in [1, 6, 8]:
                answer = 1 - answer  # 역채점 (0→1, 1→0) - 이진 응답이므로
            
            responses.append(answer)
            total_score += answer
        
        # 결과 해석
        result = {}
        if total_score < 4:
            result['severity'] = '정상'
            result['description'] = '우울증이 없는 상태입니다.'
            result['recommendation'] = '현재 상태를 유지하세요.'
            result['risk_level'] = 'low'
        elif total_score < 7:
            result['severity'] = '경도 우울증'
            result['description'] = '가벼운 우울 증상이 있습니다.'
            result['recommendation'] = '자가 관리와 정기적인 기분 체크를 권장합니다.'
            result['risk_level'] = 'low'
        elif total_score < 10:
            result['severity'] = '중등도 우울증'
            result['description'] = '중간 정도의 우울 증상이 있습니다.'
            result['recommendation'] = '전문가와 상담을 고려해보세요.'
            result['risk_level'] = 'medium'
        else:
            result['severity'] = '중증 우울증'
            result['description'] = '심한 우울 증상이 있습니다.'
            result['recommendation'] = '전문가의 도움을 받는 것이 좋습니다.'
            result['risk_level'] = 'high'
        
        # 결과 저장 (로그인한 경우만)
        if 'user_id' in session:
            save_diagnosis_result(
                session['user_id'], 
                'CESD-10-D', 
                total_score, 
                responses, 
                result
            )
        
        # 세션에 결과 저장 (결과 페이지에서 사용)
        session['diagnosis_result'] = {
            'test_type': 'CESD-10-D',
            'score': total_score,
            'responses': responses,
            'result': result,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return redirect(url_for('diagnosis.result'))
    
    # GET 요청 처리 (설문지 표시)
    return render_template('diagnosis/cesd10.html', 
                          title='mindLog - CESD-10-D 자가진단',
                          questions=CESD10_QUESTIONS)

@diagnosis_bp.route('/result')
def result():
    """자가진단 결과 페이지"""
    # 세션에서 결과 가져오기
    diagnosis_result = session.get('diagnosis_result')
    
    if not diagnosis_result:
        flash('자가진단 결과가 없습니다. 먼저 자가진단을 완료해주세요.', 'warning')
        return redirect(url_for('diagnosis.index'))
    
    # 결과 표시
    return render_template('diagnosis/results.html',
                          title='mindLog - 자가진단 결과',
                          result=diagnosis_result)

@diagnosis_bp.route('/history')
def history():
    """자가진단 내역 페이지"""
    if 'user_id' not in session:
        flash('자가진단 내역을 보려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
    
    # 사용자의 자가진단 내역 가져오기
    diagnosis_history = get_diagnosis_history(session['user_id'])
    
    return render_template('diagnosis/history.html',
                          title='mindLog - 자가진단 내역',
                          history=diagnosis_history)

@diagnosis_bp.route('/chat_diagnosis', methods=['GET', 'POST'])
def chat_diagnosis():
    """챗봇 기반 자연어 자가진단 페이지"""
    if 'user_id' not in session:
        flash('자가진단을 이용하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        user_text = request.form.get('user_text', '')
        
        if not user_text:
            flash('내용을 입력해주세요.', 'warning')
            return render_template('diagnosis/chat_diagnosis.html', title='mindLog - 자연어 자가진단')
        
        # 사용자 텍스트 기반 우울증 점수 계산 (예시 - 실제로는 NLP 모델 필요)
        # 여기서는 간단한 키워드 기반 점수 계산
        depression_keywords = ['우울', '슬픔', '무기력', '불행', '절망', '지침', '실패', '후회', '불안', '고립']
        score = 0
        for keyword in depression_keywords:
            if keyword in user_text:
                score += 1
        
        # 위험 수준 판단
        risk_level = 'low'
        severity = '정상'
        
        if score >= 3 and score < 5:
            severity = '경도 우울증'
            risk_level = 'low'
        elif score >= 5 and score < 7:
            severity = '중등도 우울증'
            risk_level = 'medium'
        elif score >= 7:
            severity = '중증 우울증'
            risk_level = 'high'
        
        # 결과 생성
        result = {
            'severity': severity,
            'score': score,
            'risk_level': risk_level,
            'description': f'{severity} 증상이 감지되었습니다.',
            'recommendation': get_recommendation(risk_level)
        }
        
        # 결과 저장
        if 'user_id' in session:
            save_diagnosis_result(
                session['user_id'],
                'CHAT',
                score,
                [],
                result,
                user_text
            )
        
        # 세션에 결과 저장
        session['diagnosis_result'] = {
            'test_type': 'CHAT',
            'score': score,
            'responses': [],
            'result': result,
            'user_text': user_text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return redirect(url_for('diagnosis.result'))
    
    # GET 요청 처리
    return render_template('diagnosis/chat_diagnosis.html', title='mindLog - 자연어 자가진단')

# 유틸리티 함수
def save_diagnosis_result(user_id, test_type, score, responses, result, user_text=None):
    """자가진단 결과 저장"""
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
            # 테이블명과 DB 스키마 확인 필요
            sql = """
            INSERT INTO SELFDIAGNOSIS 
            (USER_SEQ, DIAGNOSIS_DATE, DEPRESSION_SCORE, RISK_LEVEL, USER_TEXT) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                user_id,
                datetime.now(),
                score,
                result.get('risk_level', 'low'),
                user_text or json.dumps(responses)
            ))
            conn.commit()
    except Exception as e:
        print(f"진단 결과 저장 오류: {e}")
    finally:
        if conn:
            conn.close()

def get_diagnosis_history(user_id):
    """사용자의 자가진단 내역 가져오기"""
    conn = None
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            db=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cur:
            # 테이블명과 DB 스키마 확인 필요
            sql = """
            SELECT DIAGNOSIS_SEQ, DIAGNOSIS_DATE, DEPRESSION_SCORE, RISK_LEVEL 
            FROM SELFDIAGNOSIS 
            WHERE USER_SEQ = %s 
            ORDER BY DIAGNOSIS_DATE DESC
            """
            cur.execute(sql, (user_id,))
            history = cur.fetchall()
            
            return history
    except Exception as e:
        print(f"진단 내역 조회 오류: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_recommendation(risk_level):
    """위험 수준에 따른 권장사항 제공"""
    if risk_level == 'high':
        return "심한 우울 증상이 있습니다. 전문가의 도움을 받는 것이 좋습니다. 가까운 정신건강복지센터나 상담센터를 방문해보세요."
    elif risk_level == 'medium':
        return "중간 정도의 우울 증상이 있습니다. 전문가와 상담을 고려해보세요. 규칙적인 운동과 충분한 수면이 도움이 될 수 있습니다."
    else:
        return "경미한 우울 증상이 있거나 정상 범위입니다. 규칙적인 생활과 스트레스 관리를 통해 현재 상태를 유지하세요."