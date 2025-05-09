from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import pymysql
from datetime import datetime
from config import Config
import re
from app.ai.chatbot import ChatbotService, user_chat_buffer

# 챗봇 블루프린트 정의
chatbot_bp = Blueprint('chatbot', __name__)

chatbot_service = ChatbotService()

@chatbot_bp.route('/')
def index():
    """챗봇 메인 페이지"""
    if 'user_id' not in session:
        flash('챗봇 기능을 이용하려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
    # 이전 대화 내역 불러오기
    chat_history = get_chat_history(session['user_id'])
    return render_template('chatbot/chat.html', 
                          title='mindLog - 마음챙김 챗봇',
                          chat_history=chat_history)

@chatbot_bp.route('/send', methods=['POST'])
def send_message():
    """챗봇에게 메시지 전송"""
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    
    # 요청 데이터 처리
    user_message = request.form.get('message', '')
    
    if not user_message:
        return jsonify({"error": "메시지가 비어있습니다."}), 400
    
    # 사용자 메시지 저장
    save_message(session['user_id'], user_message, True)
    
    # ChatbotService로 응답 생성
    bot_response = chatbot_service.handle_input(user_message, user_id=session['user_id'])
    
    # 챗봇 응답 저장
    save_message(session['user_id'], bot_response, False)
    
    return jsonify({
        "userMessage": user_message,
        "botResponse": bot_response,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@chatbot_bp.route('/history')
def history():
    """챗봇 대화 내역 페이지"""
    if 'user_id' not in session:
        flash('대화 내역을 보려면 로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login'))
    
    # 대화 내역 불러오기
    chat_history = get_chat_history(session['user_id'])
    
    return render_template('chatbot/history.html',
                          title='mindLog - 챗봇 대화 내역',
                          chat_history=chat_history)

@chatbot_bp.route('/save_buffer', methods=['POST'])
def save_buffer():
    if 'user_id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    user_id = session['user_id']
    chatbot_service = ChatbotService()
    # 남은 메시지 있으면 저장
    if user_id in user_chat_buffer and user_chat_buffer[user_id]:
        concat_text = '\n'.join(user_chat_buffer[user_id])
        depression_result = chatbot_service.depression_model.predict(concat_text)
        prob = depression_result['depression_probability']
        risk_level = depression_result['label_name']
        chatbot_service.save_diagnosis_result(user_id, int(prob * 100), risk_level, concat_text)
        user_chat_buffer[user_id] = []
        return jsonify({'result': 'saved'})
    return jsonify({'result': 'no_data'})

# 유틸리티 함수
def get_chat_history(user_id, limit=50):
    """사용자의 대화 내역 가져오기"""
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
            # 최근 대화 내역 조회
            sql = """
            SELECT MESSAGE_TEXT, IS_FROM_USER, TIMESTAMP
            FROM CHATMESSAGES
            WHERE USER_SEQ = %s
            ORDER BY TIMESTAMP DESC
            LIMIT %s
            """
            cur.execute(sql, (user_id, limit))
            messages = cur.fetchall()
            
            # 시간순으로 정렬
            messages.reverse()
            
            return messages
    except Exception as e:
        print(f"대화 내역 조회 오류: {e}")
        return []
    finally:
        if conn:
            conn.close()

def save_message(user_id, message, is_from_user):
    """메시지 저장"""
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
            # 메시지 저장
            sql = """
            INSERT INTO CHATMESSAGES (USER_SEQ, MESSAGE_TEXT, IS_FROM_USER, TIMESTAMP)
            VALUES (%s, %s, %s, %s)
            """
            cur.execute(sql, (user_id, message, is_from_user, datetime.now()))
            conn.commit()
    except Exception as e:
        print(f"메시지 저장 오류: {e}")
    finally:
        if conn:
            conn.close()

def check_risk_keywords(message):
    """위험 키워드 체크"""
    # 위험 키워드 목록
    high_risk_keywords = ['자살', '죽고싶다', '죽고 싶다', '자해', '목숨', '끝내고 싶다']
    medium_risk_keywords = ['절망', '우울', '괴롭다', '괴로움', '고통', '힘들다']
    
    # 메시지 소문자로 변환
    message_lower = message.lower()
    
    # 위험도 체크
    for keyword in high_risk_keywords:
        if keyword in message_lower:
            return 'high'
    
    for keyword in medium_risk_keywords:
        if keyword in message_lower:
            return 'medium'
    
    return 'low'

def generate_crisis_response():
    """위기 상황 응답 생성"""
    responses = [
        "지금 매우 힘든 상황에 있는 것 같습니다. 혼자 힘들어하지 마시고 전문가의 도움을 받는 것이 중요합니다. "
        "지금 바로 자살예방 핫라인(1393)이나 정신건강 위기 상담전화(1577-0199)로 연락해주세요. "
        "24시간 전문가와 상담이 가능합니다.",
        
        "당신의 감정과 고통을 이해합니다. 하지만 지금은 전문적인 도움이 필요한 순간입니다. "
        "가까운 정신건강복지센터나 자살예방센터(1393)에 연락하여 전문가의 도움을 받으세요. "
        "당신은 혼자가 아닙니다.",
        
        "지금 위험한 생각을 하고 계신다면, 즉시 주변의 도움을 청하세요. "
        "자살예방 핫라인(1393) 또는 정신건강 위기 상담전화(1577-0199)는 24시간 당신의 이야기를 들어줄 준비가 되어 있습니다. "
        "또한 가까운 응급실을 방문하는 것도 좋은 선택입니다."
    ]
    
    import random
    return random.choice(responses)

def generate_bot_response(message, risk_level):
    """챗봇 응답 생성"""
    # 실제 구현에서는 LLM을 사용하여 응답 생성
    # 여기서는 간단한 예시 응답만 제공
    
    if risk_level == 'medium':
        responses = [
            "지금 힘든 시간을 보내고 계신 것 같습니다. 괜찮으실까요? 더 자세히 이야기해주시겠어요?",
            "마음이 많이 무거우신 것 같습니다. 언제부터 이런 감정을 느끼셨나요?",
            "그런 감정을 느끼는 것은 자연스러운 일입니다. 혹시 이런 감정이 자주 드시나요?",
            "많이 지치고 힘드실 것 같습니다. 조금 더 구체적으로 어떤 상황인지 말씀해주시면 더 도움이 될 수 있을 것 같아요."
        ]
    else:
        if "안녕" in message or "하이" in message:
            responses = [
                "안녕하세요! 오늘 기분이 어떠신가요?",
                "반갑습니다! 오늘 하루는 어떻게 지내셨나요?",
                "안녕하세요! 무엇을 도와드릴까요?"
            ]
        elif "기분" in message or "우울" in message:
            responses = [
                "기분이 어떻게 변화가 있으셨나요? 구체적으로 말씀해주시면 더 도움이 될 수 있어요.",
                "언제부터 그런 기분이 드셨나요? 특별한 계기가 있었을까요?",
                "우울한 기분이 들 때 어떤 활동이 도움이 되시나요?"
            ]
        elif "고민" in message or "걱정" in message:
            responses = [
                "어떤 걱정이 있으신지 더 말씀해주실 수 있을까요?",
                "그런 고민이 있으셨군요. 다른 사람들과 이야기해보셨나요?",
                "걱정이 많으시군요. 제가 어떻게 도움을 드릴 수 있을까요?"
            ]
        else:
            responses = [
                "더 자세히 말씀해주시겠어요?",
                "그렇군요. 다른 생각이나 느낌이 있으신가요?",
                "이해합니다. 다른 이야기도 해주세요.",
                "더 들어보고 싶어요. 계속해서 말씀해주시겠어요?"
            ]
    
    import random
    return random.choice(responses)